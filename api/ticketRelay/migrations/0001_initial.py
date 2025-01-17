# Generated by Django 4.0.1 on 2022-09-16 00:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_status', models.CharField(choices=[('Q', 'Queued'), ('A', 'Approved'), ('D', 'Denied'), ('N', 'Notes')], default='Q', max_length=1)),
                ('worker_action_status', models.CharField(choices=[('W', 'Waiting for Feedback'), ('P', 'Purchase Confirmed'), ('C', 'Cancelled')], default='W', max_length=1)),
                ('ce_id', models.CharField(max_length=350)),
                ('uuid', models.CharField(max_length=350)),
                ('timer', models.IntegerField()),
                ('worker_email', models.CharField(max_length=200)),
                ('reseller_website', models.CharField(max_length=200)),
                ('reserved_at', models.CharField(max_length=200)),
                ('reserved_at_Date', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_date', models.CharField(max_length=400)),
                ('event_name', models.CharField(max_length=300)),
                ('ticket_price', models.CharField(max_length=300)),
                ('ticket_quantity', models.CharField(max_length=300)),
                ('venue', models.CharField(max_length=400)),
                ('seat_row', models.CharField(max_length=300)),
                ('seat_numbers', models.CharField(max_length=300)),
                ('seat_section', models.CharField(max_length=300)),
                ('note', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ['feedback_status'],
            },
        ),
    ]