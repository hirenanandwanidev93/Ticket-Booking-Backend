# Generated by Django 4.0.1 on 2023-04-11 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticketRelay', '0003_ticket_feedback_received_by_ce'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='feedback_received_by_CE',
        ),
    ]
