# CELERY & DJANGO IMPORTS
from celery import shared_task  # Allows defining reusable Celery background tasks

from django.core.mail import send_mail  # Used to send notification emails
from django.conf import settings        # Access project email settings

# ---------------------------
# APP MODELS
# ---------------------------
from .models import (
    Ticket,
    MLPredictionHistory,
    SLAReport,
    TicketActivity
)

from users.models import User  # User model for agent assignment

# ---------------------------
# ML MODELS
# ---------------------------
from .ml.model import predict_priority            # Rule-based ML prediction
from .ml.tfidf_model import (
    fit_model_on_tickets,
    predict_scores_for_tickets
)


# =====================================================
# PRIORITY PREDICTION TASK (RULE-BASED ML)
# =====================================================
@shared_task
def enqueue_priority_prediction(ticket_id):
    """
    Predicts ticket priority using keyword-based ML logic
    and stores prediction history.
    Runs asynchronously to avoid blocking API response.
    """
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        # Combine title + description for prediction
        pred, score = predict_priority(
            (ticket.title or '') + ' ' + (ticket.description or '')
        )

        # Update ticket priority
        ticket.priority = pred
        ticket.save()

        # Store ML prediction history
        MLPredictionHistory.objects.create(
            ticket=ticket,
            predicted_priority=pred,
            confidence_score=score,
            model_version='v1'
        )

    except Exception as e:
        print('priority task error:', e)


# =====================================================
# EMAIL NOTIFICATION TASK
# =====================================================
@shared_task
def send_ticket_created_email(ticket_id):
    """
    Sends email notification to the ticket creator
    after ticket creation.
    """
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        subject = f"Ticket Created: {ticket.ticket_id}"
        body = (
            f"Your ticket has been created successfully.\n\n"
            f"Ticket ID: {ticket.ticket_id}\n"
            f"Priority: {ticket.priority}"
        )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.created_by.email]
        )

    except Exception as e:
        print("Email sending failed:", e)


# =====================================================
# AUTO ASSIGN AGENT TASK
# =====================================================
@shared_task
def auto_assign_agent(ticket_id):
    """
    Automatically assigns the first available active agent
    to the ticket and logs activity.
    """
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        # Fetch available agent
        agent = User.objects.filter(
            role='agent',
            is_active=True
        ).order_by('id').first()

        if agent:
            ticket.assigned_to = agent
            ticket.save()

            # Log assignment activity
            TicketActivity.objects.create(
                ticket=ticket,
                actor=None,
                comment=f'Auto-assigned to {agent.username}',
                old_status='',
                new_status=ticket.status
            )

    except Exception as e:
        print('auto assign error:', e)


# =====================================================
# DAILY SLA REPORT TASK
# =====================================================
@shared_task
def generate_daily_sla_report():
    """
    Generates daily SLA report containing
    total and breached tickets.
    """
    from django.utils import timezone

    today = timezone.now().date()
    total = Ticket.objects.count()
    breached = Ticket.objects.filter(status='open').count()

    SLAReport.objects.create(
        report_date=today,
        total_tickets=total,
        breached_tickets=breached,
        file_path=''
    )


# =====================================================
# TF-IDF BASED PRIORITY RANKING TASK
# =====================================================
@shared_task
def run_tfidf_ranking(threshold_high=0.35, threshold_med=0.18, limit=1000):
    """
    Uses TF-IDF cosine similarity to rank ticket urgency.
    Assigns priority based on similarity score thresholds.
    """
    try:
        # Fetch latest tickets
        tickets = list(
            Ticket.objects.all().order_by('-created_at')[:limit]
        )

        # Prepare text corpus
        texts = [
            (t.title or '') + ' ' + (t.description or '')
            for t in tickets
        ]

        if not texts:
            return 'no tickets'

        # Train TF-IDF model
        fit_model_on_tickets(texts)

        # Predict urgency scores
        scores = predict_scores_for_tickets(texts)

        for ticket, score in zip(tickets, scores):

            # Skip manually assigned priorities
            if ticket.priority in ['high', 'medium', 'low']:
                continue

            # Determine priority based on score
            if score >= threshold_high:
                pred = 'high'
            elif score >= threshold_med:
                pred = 'medium'
            else:
                pred = 'low'

            # Save prediction history
            MLPredictionHistory.objects.create(
                ticket=ticket,
                predicted_priority=pred,
                confidence_score=float(score),
                model_version='tfidf-v1'
            )

            # Update ticket priority
            ticket.priority = pred
            ticket.save()

        return f'processed {len(tickets)} tickets'

    except Exception as e:
        print('tfidf ranking error:', e)
        return str(e)
