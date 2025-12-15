from django.db import models
from django.conf import settings

# Custom user model (used for authentication and role-based access)
User = settings.AUTH_USER_MODEL


class Category(models.Model):
    """
    Stores ticket categories like IT, Billing, Network, etc.
    Used to classify tickets.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """
    Core ticket model which stores all ticket-related information.
    """

    # Priority levels
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    )

    # Ticket lifecycle statuses
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    )

    # Auto-generated ticket reference ID
    ticket_id = models.CharField(max_length=20, unique=True)

    # Ticket details
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Optional category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Priority and status
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )

    # Ticket ownership and assignment
    created_by = models.ForeignKey(
        User,
        related_name='created_tickets',
        on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        User,
        related_name='assigned_tickets',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"


class Attachment(models.Model):
    """
    Stores files uploaded with a ticket (screenshots, logs, etc.)
    """
    ticket = models.ForeignKey(
        Ticket,
        related_name='attachments',
        on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TicketActivity(models.Model):
    """
    Maintains ticket history such as status change,
    comments, and actions performed by users.
    """
    ticket = models.ForeignKey(
        Ticket,
        related_name='activities',
        on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField(blank=True)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SLAReport(models.Model):
    """
    Stores SLA analytics data such as breach count
    and generated report file details.
    """
    report_date = models.DateField()
    total_tickets = models.IntegerField()
    breached_tickets = models.IntegerField()
    file_path = models.CharField(max_length=400, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)


class MLPredictionHistory(models.Model):
    """
    Stores ML model prediction results for each ticket,
    used for auditing and improvement.
    """
    ticket = models.ForeignKey(
        Ticket,
        related_name='predictions',
        on_delete=models.CASCADE
    )
    predicted_priority = models.CharField(max_length=20)
    model_version = models.CharField(max_length=50, blank=True)
    confidence_score = models.FloatField(default=0.0)
    run_at = models.DateTimeField(auto_now_add=True)
