# django_filters is used to create dynamic filters for API requests
import django_filters

# Import Ticket model for filtering ticket data
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    """
    This filter class is used to apply query-based filtering
    on Ticket APIs (used in list and analytics views).
    """

    # Filter tickets by created date range (from_date → to_date)
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')

    # Case-insensitive filter for ticket status (open, resolved, etc.)
    status = django_filters.CharFilter(lookup_expr='iexact')

    # Case-insensitive filter for ticket priority (high, medium, low)
    priority = django_filters.CharFilter(lookup_expr='iexact')

    # Filter tickets by assigned agent ID
    assigned_to = django_filters.NumberFilter()

    # Custom search filter for title and description
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        # Connect this filter with Ticket model
        model = Ticket

        # Fields allowed for filtering via query params
        fields = ['status', 'priority', 'assigned_to']

    def filter_search(self, queryset, name, value):
        """
        Custom search logic:
        Filters tickets where search text appears
        in either title or description.
        """
        return (
            queryset.filter(title__icontains=value) |
            queryset.filter(description__icontains=value)
        )
