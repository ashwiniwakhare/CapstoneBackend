from rest_framework import serializers
from .models import Category, Ticket, TicketActivity, Attachment, MLPredictionHistory
from users.serializers import UserSerializer


# ---------------------------
# CATEGORY SERIALIZER
# ---------------------------
class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes ticket categories.
    Used for listing and displaying category details.
    """
    class Meta:
        model = Category
        fields = "__all__"


# ---------------------------
# ATTACHMENT SERIALIZER
# ---------------------------
class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializes ticket attachments and returns
    a downloadable file URL.
    """
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        """
        Builds absolute file URL if request context is available.
        """
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']


# ---------------------------
# TICKET ACTIVITY SERIALIZER
# ---------------------------
class TicketActivitySerializer(serializers.ModelSerializer):
    """
    Serializes ticket activity logs
    like status changes and comments.
    """
    actor = UserSerializer(read_only=True)

    class Meta:
        model = TicketActivity
        fields = "__all__"


# ---------------------------
# CREATE TICKET SERIALIZER (POST)
# ---------------------------
class CreateTicketSerializer(serializers.ModelSerializer):
    """
    Serializer used only while creating tickets.
    Handles attachments and auto ticket ID generation.
    """
    attachments = AttachmentSerializer(many=True, read_only=True)

    # Accept category as ID instead of full object
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category_id', 'attachments']

    def create(self, validated_data):
        """
        Generates unique ticket ID and saves attachments.
        """
        import uuid
        validated_data['ticket_id'] = 'TCK-' + str(uuid.uuid4())[:8].upper()
        ticket = super().create(validated_data)

        # Save uploaded files
        attachments = self.context.get('attachments')
        if attachments:
            for file in attachments:
                Attachment.objects.create(ticket=ticket, file=file)

        return ticket


# ---------------------------
# MAIN TICKET SERIALIZER (GET)
# ---------------------------
class TicketSerializer(serializers.ModelSerializer):
    """
    Full ticket serializer used for listing and viewing tickets.
    """
    created_by = UserSerializer(read_only=True)
    activities = TicketActivitySerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    # Nested category details for frontend
    category = CategorySerializer(read_only=True)

    # Accept category update via ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Custom representation for assigned agent
    assigned_to = serializers.SerializerMethodField()

    def get_assigned_to(self, obj):
        """
        Returns limited agent details.
        """
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "username": obj.assigned_to.username,
                "email": obj.assigned_to.email,
            }
        return None

    class Meta:
        model = Ticket
        fields = "__all__"
