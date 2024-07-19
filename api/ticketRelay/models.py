from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    FEEDBACK_DEFAULT = 'Q'
    FEEDBACK_CHOICES = [
        (FEEDBACK_DEFAULT, 'Queued'),
        ('A', 'Approved'),
        ('D', 'Denied'),
        ('N', 'Notes'),
    ]
    WORKER_ACTION_DEFAULT = 'W'
    WORKER_ACTION_CHOICES = [
        (WORKER_ACTION_DEFAULT, 'Waiting for Feedback'),
        ('P', 'Purchase Confirmed'),
        ('C', 'Cancelled')
    ]
    feedback_status = models.CharField(
        max_length=1, choices=FEEDBACK_CHOICES, default=FEEDBACK_DEFAULT)
    worker_action_status = models.CharField(
        max_length=1, choices=WORKER_ACTION_CHOICES, default=WORKER_ACTION_DEFAULT)

    ce_id = models.CharField(max_length=350)
    
    uuid = models.CharField(max_length=350)
    
    timer = models.IntegerField()

    worker_email = models.CharField(max_length=200)
    
    reseller_website = models.CharField(max_length=200)

    reserved_at = models.CharField(max_length=200)

    reserved_at_Date = models.DateTimeField(default=timezone.now)

    event_date = models.CharField(max_length=400)

    event_name = models.CharField(max_length=300)

    ticket_price = models.CharField(max_length=300)
    
    ticket_quantity = models.CharField(max_length=300)
    
    venue = models.CharField(max_length=400)
    
    seat_row = models.CharField(max_length=300)

    seat_numbers = models.CharField(max_length=300)

    seat_section = models.CharField(max_length=300)

    feedback_received_by_CE = models.BooleanField(default=False)

    ticket_action_timestamp = models.CharField(max_length=400, null=True)

    delivery_method = models.CharField(max_length=300, null=True)

    note = models.CharField(max_length=500)
    # Create a filter for sorting table by chosen field a-z
    class Meta:
        ordering = ['feedback_status']
    
    @property
    def user_email(self):
        return self.worker_email

class PushNotificationToken(models.Model):
    token = models.CharField(max_length=600)
    user_id = models.IntegerField()