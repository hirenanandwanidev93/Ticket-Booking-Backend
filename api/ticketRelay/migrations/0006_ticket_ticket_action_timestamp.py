# Generated by Django 4.0.1 on 2023-04-13 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketRelay', '0005_ticket_feedback_received_by_ce'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='ticket_action_timestamp',
            field=models.CharField(max_length=400, null=True),
        ),
    ]