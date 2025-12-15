# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------
# DRF core components for building API views and viewsets
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

# Django utilities
from django.utils import timezone  # for datetime operations
from django.db.models import Count  # aggregation
from django.db.models.functions import TruncDate  # for truncating datetime to date

# DRF filtering and ordering
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# Import tasks for asynchronous execution
from .tasks import run_tfidf_ranking, send_ticket_created_email

# Import models and serializers
from .models import Ticket, Category
from .serializers import TicketSerializer, CreateTicketSerializer, CategorySerializer
from .filters import TicketFilter  # custom filter class for tickets


# ---------------------------------------------------------
# TICKET VIEWSET
# ---------------------------------------------------------
class TicketViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Tickets.
    - Uses different serializers for creation and other actions.
    - Sends async email when a ticket is created.
    """
    queryset = Ticket.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return CreateTicketSerializer if self.action == 'create' else TicketSerializer

    def create(self, request, *args, **kwargs):
        # Handle multiple file attachments
        files = request.FILES.getlist('file')
        serializer = self.get_serializer(
            data=request.data,
            context={'attachments': files}
        )
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save(created_by=request.user)
        # Send email asynchronously after ticket creation
        send_ticket_created_email.delay(ticket.id)
        return Response(TicketSerializer(ticket).data, status=201)

    def perform_update(self, serializer):
        # Automatically assign updated ticket to the current user
        serializer.save(assigned_to=self.request.user)


# ---------------------------------------------------------
# CATEGORY VIEWSET
# ---------------------------------------------------------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoints for ticket categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------
# TICKET LIST VIEW WITH FILTERS
# ---------------------------------------------------------
class TicketListView(generics.ListAPIView):
    """
    Custom filtered list view for tickets.
    Supports:
    - ?mine=true → tickets created by current user
    - ?assigned_to=me → tickets assigned to current user
    """
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TicketFilter
    ordering_fields = ['created_at', 'priority']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if self.request.query_params.get("mine") == "true":
            qs = qs.filter(created_by=user)

        if self.request.query_params.get("assigned_to") == "me":
            qs = qs.filter(assigned_to=user)

        return qs


# ---------------------------------------------------------
# TICKET ANALYTICS VIEW
# ---------------------------------------------------------
class TicketAnalyticsView(APIView):
    """
    Provides ticket analytics for dashboards.
    Supports multiple actions via query param 'action':
    1. volume_by_date → number of tickets per day for last 30 days
    2. sla_breach_rate → percentage of open tickets >24hrs
    3. agent_performance → resolved tickets per agent
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        action = request.query_params.get("action")

        # -----------------------------
        # 1 — VOLUME LAST 30 DAYS
        # -----------------------------
        if action == "volume_by_date":
            today = timezone.now().date()
            start = today - timezone.timedelta(days=30)

            qs = (
                Ticket.objects.filter(created_at__date__gte=start)
                .annotate(date=TruncDate("created_at"))
                .values("date")
                .annotate(count=Count("id"))
                .order_by("date")
            )

            data = [{'date': str(row["date"]), 'count': row["count"]} for row in qs]
            return Response(data)

        # -----------------------------
        # 2 — SLA BREACH (open > 24 hrs)
        # -----------------------------
        if action == "sla_breach_rate":
            now = timezone.now()
            cutoff = now - timezone.timedelta(hours=24)

            total = Ticket.objects.count()
            breached = Ticket.objects.filter(status="open", created_at__lt=cutoff).count()

            rate = round((breached / total * 100), 2) if total else 0

            return Response({
                "total": total,
                "breached": breached,
                "breach_rate_percent": rate
            })

        # -----------------------------
        # 3 — AGENT PERFORMANCE
        # -----------------------------
        if action == "agent_performance":
            qs = (
                Ticket.objects.filter(
                    status__in=["resolved", "closed"],
                    assigned_to__isnull=False
                )
                .values("assigned_to__username")
                .annotate(resolved=Count("id"))
                .order_by("-resolved")
            )

            data = [
                {
                    "agent": row["assigned_to__username"],
                    "resolved": row["resolved"]
                }
                for row in qs
            ]

            return Response(data)


# ---------------------------------------------------------
# TRIGGER TF-IDF RANKING (ASYNC)
# ---------------------------------------------------------
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def trigger_tfidf_ranking(request):
    """
    Triggers the TF-IDF ranking task asynchronously.
    """
    run_tfidf_ranking.delay()
    return Response({"status": "started"})


# ---------------------------------------------------------
# CLEAN SLA BREACH ENDPOINT
# ---------------------------------------------------------
@api_view(["GET"])
def sla_breach_rate(request):
    """
    Returns SLA breach metrics:
    - total tickets
    - tickets open >24 hrs
    - breach rate %
    """
    now = timezone.now()
    cutoff = now - timezone.timedelta(hours=24)

    total = Ticket.objects.count()
    breached = Ticket.objects.filter(status="open", created_at__lt=cutoff).count()

    percent = round((breached / total * 100), 2) if total else 0

    return Response({
        "total_tickets": total,
        "breached_tickets": breached,
        "breach_rate_percent": percent
    })
