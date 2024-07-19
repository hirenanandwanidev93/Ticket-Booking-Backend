from xml.dom.minidom import Identified
from .models import Ticket, PushNotificationToken
from rest_framework import serializers


class TicketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    ce_id = serializers.CharField(read_only=False)
    uuid = serializers.CharField(read_only=False)
    timer = serializers.IntegerField(read_only=False)
    feedback_status = serializers.CharField(read_only=False)
    worker_action_status = serializers.CharField(read_only=False)
    worker_email = serializers.CharField(read_only=True)
    reserved_at = serializers.CharField(read_only=True)
    event_date = serializers.CharField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    ticket_price = serializers.CharField(read_only=True)
    ticket_quantity = serializers.CharField(read_only=True)
    venue = serializers.CharField(read_only=True)
    seat_row = serializers.CharField(read_only=True)
    seat_numbers = serializers.CharField(read_only=True)
    seat_section = serializers.CharField(read_only=True)
    reseller_website = serializers.CharField(read_only=True)
    note = serializers.CharField(read_only=True)
    feedback_received_by_CE = serializers.BooleanField(read_only=False, required=False)
    ticket_action_timestamp = serializers.CharField(read_only=True, required=False)
    delivery_method = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'uuid',
            'ce_id',
            'feedback_status',
            "timer",
            'reserved_at',
            'worker_email',
            'event_date',
            'event_name',
            'ticket_price',
            'ticket_quantity',
            'seat_row',
            'seat_numbers',
            'seat_section',
            'venue',
            'worker_action_status',
            'reseller_website',
            'note',
            'feedback_received_by_CE',
            'ticket_action_timestamp',
            'delivery_method'
        ]


class PushTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=False)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = PushNotificationToken
        fields = ['token', 'user_id']


class PriceSerializer(serializers.ModelSerializer):
    ticket_price = serializers.CharField(read_only=True)
    reserved_at = serializers.CharField(read_only=True)
    class Meta:
        model = Ticket
        fields = ["ticket_price", "reserved_at"]
