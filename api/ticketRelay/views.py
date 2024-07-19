from django.shortcuts import render
from django.views.generic.base import TemplateView
from api.ticketRelay.serializers import TicketSerializer, PriceSerializer, PushTokenSerializer
from api.ticketRelay.models import Ticket, PushNotificationToken
from django.views.decorators.csrf import csrf_exempt
import json
import time
import pytz
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import date, datetime, timedelta
import mimetypes
import os
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView
import traceback
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import json
import traceback
import firebase_admin
from firebase_admin import credentials, messaging

with open('./key.json') as json_file:
    keys = json.load(json_file)
cred = credentials.Certificate(keys)
firebase_admin.initialize_app(cred)


def sendPushNotification(title, message):
    print("Sending push notifications")
    if isinstance(message, dict):
        print("Is dictionary: %s" % message)
        if message['worker_action_status'] == "C":
            message['worker_action_status'] = "Cancelled"
        elif message['worker_action_status'] == "P":
            message['worker_action_status'] = "Purchased"
        message = "Event: " + message['eventName'] + \
            "\nStatus: " + message["worker_action_status"]
    allPushTokens = PushNotificationToken.objects.all()
    print("All tokens in database: " + str(allPushTokens.count()))
    for pushToken in allPushTokens:
        print(pushToken.token)
        print(message)
        try:
            # Define the notification payload
            message1 = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=str(message)),
                token=pushToken.token
            )
            # Send the message
            response = messaging.send(message1)
            #print('Successfully sent push notification')
        except Exception as e:
            print(
                'Failed to send push notifications with error below. Deleting token next')
            print(e)
            PushNotificationToken.objects.filter(
                token=pushToken.token).delete()


class WsViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        data = Ticket.objects.filter(
            ~Q(feedback_status='Q')).order_by("-reserved_at_Date").values()

        serializer = TicketSerializer(
            data, context={'request': request}, many=True)

        return Response(serializer.data)


class TicketViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        data = Ticket.objects.filter(
            ~Q(feedback_status='Q')).order_by("-reserved_at").values()

        serializer = TicketSerializer(
            data, context={'request': request}, many=True)

        return Response(serializer.data)


class VerifyApiKeys(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        extension_key = request.GET.get('Api_Key')
        secret = "1234567-ticketRelayExtension-890"
        if extension_key == secret:
            return JsonResponse({"api_key_valid": True})
        else:
            return JsonResponse({"api_key_valid": False})


class NewTicketPage(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def create(self, request, *args, **kwargs):
        request_body = json.loads(request.body)
        print(request_body)
        return JsonResponse({"status": "success", "message": "Received Correctly", "code": 200})


def send_message_to_frontend(header, data):
    print("Sending message to frontend...")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'All-FrontEnd-Users',
        {
            'type': 'send_message_to_frontend',
            'message': {
                'header': header,
                'data': data
            }
        }
    )
    print("SOCKET message sent")


def send_message_to_worker(header, data, CE_id):
    print("Sending message to worker...")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        CE_id,
        {
            'type': 'send_message_to_frontend',
            'message': {
                'header': header,
                'data': data
            }
        }
    )
    print("SOCKET message sent")


class TicketInQueueViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        tickets_in_Queue = Ticket.objects.filter(
            worker_action_status='W').order_by("-reserved_at_Date").values()
        serializer = TicketSerializer(tickets_in_Queue, context={
                                      'request': request}, many=True)
        valid_tickets = []
        print("Removing Expired Tickets")
        for idx, single_ticket in enumerate(serializer.data):
            if single_ticket["timer"] != 0:
                dateNow = time.time() * 1000
                dateReservedAt = int(single_ticket["reserved_at"])
                timer = single_ticket["timer"]
                expirationDate = dateReservedAt + timer
                if dateNow > expirationDate:
                    # If ticket is expired, cancel it
                    ticket = Ticket.objects.get(id=single_ticket["id"])
                    ticket.worker_action_status = "C"
                    action_timestamp = datetime.now(pytz.timezone('UTC'))
                    ticket.ticket_action_timestamp = action_timestamp 
                    ticket.save()
                else:
                    valid_tickets.append(single_ticket)
            else:
                valid_tickets.append(single_ticket)

        if (valid_tickets):
            return Response(valid_tickets)
        else:
            return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})


class GetExpiredTicketsViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        today = datetime.now(pytz.timezone('UTC')).date()
        dateRange = int(request.GET.get('daterange'))
        range = today - timedelta(days=dateRange)
        tickets_in_Queue = Ticket.objects.filter(
            worker_action_status='C', reserved_at_Date__range=[
                range, today]).order_by("-reserved_at_Date").values()
        serializer = TicketSerializer(tickets_in_Queue, context={
                                      'request': request}, many=True)

        if (serializer.data):
            return Response(serializer.data)
        else:
            return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})


#Return Expired Ticket For Particular Date Range
class GetExpiredTicketsByActualDateViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if not to_date:
            to_date = datetime.now(pytz.timezone('UTC')).date()
        if not from_date:
            return JsonResponse({"status": "error", "message": "Please Define Valid Date-Range", "code": 400})
        tickets_in_Queue = Ticket.objects.filter(
            worker_action_status='C', reserved_at_Date__range=[
                from_date, to_date]).order_by("-reserved_at_Date").values()
        serializer = TicketSerializer(tickets_in_Queue, context={
                                      'request': request}, many=True)

        if (serializer.data):
            return Response(serializer.data)
        else:
            return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})


class download_CE(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define text file name
        filename = 'CE_1.04.zip'
        # Define the full file path
        filepath = BASE_DIR + '/static/' + filename
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response


class download_latest_CE(TemplateView):
    template_name = "download_CE.html"


def read_file(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data


def read_json(path):
    return json.loads(read_file(path))


class latest_CE_version_available(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *arg1s, **kwargs):
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define text file name
        filename = 'versionControl.json'
        # Define the full file path
        filepath = BASE_DIR + '/static/' + filename
        versionControl = read_json(filepath)
        return JsonResponse(versionControl)


class TicketCompletedActionViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        today = datetime.now(pytz.timezone('UTC')).date()
        dateRange = int(request.GET.get('daterange'))
        range = today - timedelta(days=dateRange)
        tickets_in_Queue = Ticket.objects.filter(
            worker_action_status='P', reserved_at_Date__range=[
                range, today]).order_by("-reserved_at_Date").values()
        serializer = TicketSerializer(tickets_in_Queue, context={
                                      'request': request}, many=True)

        if (serializer.data):
            return Response(serializer.data)
        else:
            return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})

#Return Completed Ticket For Particular Date Range
class TicketCompletedByActualDateActionViewSet(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if not to_date:
            to_date = datetime.now(pytz.timezone('UTC')).date()
        if not from_date:
            return JsonResponse({"status": "error", "message": "Please Define Valid Date-Range", "code": 400})
        tickets_in_Queue = Ticket.objects.filter(
            worker_action_status='P', reserved_at_Date__range=[
                from_date, to_date]).order_by("-reserved_at_Date").values()
        serializer = TicketSerializer(tickets_in_Queue, context={
                                      'request': request}, many=True)

        if (serializer.data):
            return Response(serializer.data)
        else:
            return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})

class dashboardInformations(
        viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        try:
            # Fetch today queued tickets
            def fetch_tickets_in_queue():
                startdate = datetime.now(pytz.timezone('UTC')).date()
                enddate = startdate + timedelta(days=1)
                sevenDaysenddate = startdate - timedelta(days=7)
                thirtyDaysenddate = startdate - timedelta(days=30)
                today_tickets_in_Queue = Ticket.objects.filter(worker_action_status='W', reserved_at_Date__range=[
                    startdate, enddate]).order_by("-reserved_at_Date").count()
                today_tickets_purchased = Ticket.objects.filter(worker_action_status='P', reserved_at_Date__range=[
                                                                startdate, enddate]).order_by("-reserved_at_Date").count()
                sevenD_tickets_purchased = Ticket.objects.filter(worker_action_status='P', reserved_at_Date__range=[
                    sevenDaysenddate, startdate]).order_by("-reserved_at_Date").count()
                thirtyD_tickets_purchased = Ticket.objects.filter(worker_action_status='P', reserved_at_Date__range=[
                    thirtyDaysenddate, startdate]).order_by("-reserved_at_Date").count()
                data = {
                    "today_tickets_in_Queue": today_tickets_in_Queue,
                    "today_tickets_purchased": today_tickets_purchased,
                    "seven_days_tickets_purchased": sevenD_tickets_purchased,
                    "thirty_days_tickets_purchased": thirtyD_tickets_purchased
                }
                return data

            def fetch_tickets_confirmed():
                print("fetch tickets confirmed")
                seven_days_purchased_tickets = datetime.now(pytz.timezone('UTC')).date() - timedelta(days=7)
                today_tickets_in_Queue = Ticket.objects.filter(worker_action_status='P', reserved_at_Date__range=[
                    seven_days_purchased_tickets, datetime.now(pytz.timezone('UTC')).date()]).values("ticket_price", "reserved_at")
                serializer = PriceSerializer(today_tickets_in_Queue, context={
                    'request': request}, many=True)
                return serializer.data
            data = fetch_tickets_in_queue()
            today_tickets_in_Queue = fetch_tickets_confirmed()
            return JsonResponse({"status": "OK", "data": data, "tickets_confirmed_7_days": today_tickets_in_Queue, "code": 200})
        except Exception:
            traceback.print_exc()
        # else:
        #     return JsonResponse({"status": "error", "message": "No tickets in queue", "code": 400})


class addNewPushUser(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    serializer_class = PushTokenSerializer

    def create(self, request, *args, **kwargs):
        request_body = json.loads(request.body)
        try:
            if PushNotificationToken.objects.filter(token=request_body["token"]).exists():
                # Entry with token='value' already exists
                return JsonResponse({"status": "success", "code": 200, "message": "Token already exists"})
            else:
                # Entry with token='value' does not exist, you can create it
                NewPushToken = PushNotificationToken()
                NewPushToken.token = request_body["token"]
                NewPushToken.user_id = request_body["user_id"]
                NewPushToken.save()
                return JsonResponse({"status": "success", "code": 200, "message": "New Push Token successfully saved"})
        except:
            print(traceback.print_exc())
            return JsonResponse({"status": "error", "code": 500, "message": "Error in saving new token in Database"})


class addNewTicketViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        def remove_expired_tickets():
            tickets_in_Queue = Ticket.objects.filter(
                worker_action_status='W').order_by("-reserved_at_Date").values()
            serializer = TicketSerializer(tickets_in_Queue, context={
                'request': request}, many=True)
            for idx, single_ticket in enumerate(serializer.data):
                dateNow = time.time() * 1000
                dateReservedAt = int(single_ticket["reserved_at"])
                if single_ticket["timer"] != 0:
                    timer = single_ticket["timer"]
                    expirationDate = dateReservedAt + timer
                    if dateNow > expirationDate:
                        # If ticket is expired, cancel it
                        ticket = Ticket.objects.get(id=single_ticket["id"])
                        ticket.worker_action_status = "C"
                        action_timestamp = datetime.now(pytz.timezone('UTC'))
                        ticket.ticket_action_timestamp = action_timestamp
                        ticket.save()
                else:
                    if dateNow - dateReservedAt >= 3600000:  # If passed more than one hour remove ticket
                        ticket = Ticket.objects.get(id=single_ticket["id"])
                        ticket.worker_action_status = "C"
                        ticket.save()

        remove_expired_tickets()
        request_body = json.loads(request.body)
        try:
            ticket = Ticket()
            ticket.reserved_at_Date = datetime.now(pytz.timezone('UTC')).date()
            ticket.worker_email = request_body["workerEmail"]
            ticket.ce_id = request_body["ce_ID"]
            ticket.uuid = request_body["uuid"]
            ticket.event_date = request_body["date"]
            ticket.timer = request_body["timer"]
            ticket.reserved_at = request_body["reserved_at"]
            ticket.event_name = request_body["eventName"]
            ticket.ticket_price = request_body["price"]
            ticket.ticket_quantity = request_body["quantity"]
            ticket.seat_row = request_body["row"]
            ticket.seat_numbers = request_body["seatNumbers"]
            ticket.seat_section = request_body["section"]
            ticket.reseller_website = request_body["reseller_website"]
            ticket.venue = request_body["venue"]
            ticket.feedback_received_by_CE = False
            ticket.delivery_method = request_body["delivery_method"]
            ticket.save()
            serializer = TicketSerializer(ticket, context={'request': request})
            send_message_to_frontend(
                "New ticket waiting for a decision", serializer.data)
            # sendPushNotification(
            #     "New ticket waiting for a decision", serializer.data["event_name"])
            return JsonResponse({"status": "success", "code": 200})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": "Missing Ticket Fields", "code": 400})


class addManagerFeedbackViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def create(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body)
            print(request_body)
            ticketId = request_body["id"]
            ticketFeedback = request_body["feedback"]
            ticketNote = request_body["note"]
            ticket = Ticket.objects.get(id=ticketId)
            ticket.feedback_status = ticketFeedback
            ticket.note = ticketNote
            ticket.feedback_received_by_CE = False
            ticket.save()
            serializer = TicketSerializer(ticket, context={'request': request})
            send_message_to_worker(
                "New Manager Feedback", serializer.data, serializer.data["ce_id"])
            return JsonResponse({"status": "success", "code": 200, "message": "Ticket Feedback Updated Successfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": e, "code": 400})


class addWorkerFeedbackViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body)
            uuid = request_body["uuid"]
            worker_action_status = request_body["worker_action_status"]
            ticket = Ticket.objects.get(uuid=uuid)
            ticket.worker_action_status = worker_action_status
            action_timestamp = datetime.now(pytz.timezone('UTC'))
            ticket.ticket_action_timestamp = action_timestamp
            ticket.save()
            send_message_to_frontend("New worker feedback", request_body)
            #sendPushNotification("New worker feedback", request_body)
            return JsonResponse({"status": "success", "code": 200, "message": "Ticket Feedback Updated Successfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": e, "code": 400})


class timerTimeOut(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body)
            action_timestamp = datetime.now(pytz.timezone('UTC'))
            print(request_body)
            uuid = request_body["uuid"]
            worker_action_status = request_body["worker_action_status"]
            ticket = Ticket.objects.get(uuid=uuid)
            ticket.worker_action_status = worker_action_status
            ticket.ticket_action_timestamp = action_timestamp
            ticket.save()
            return JsonResponse({"status": "success", "code": 200, "message": "Ticket Feedback Updated Successfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": e, "code": 400})


class confirmFeedbackReceivalViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    def create(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body)
            print(request_body)
            uuid = request_body["uuid"]
            feedback_received_by_CE = request_body["feedback_received_by_CE"]
            
            if feedback_received_by_CE not in ['True', 'False']:
                raise ValueError(f'{feedback_received_by_CE} - value must be either True or False.')
            
            ticket = Ticket.objects.filter(uuid=uuid).order_by("-reserved_at_Date")[0]
            ticket.feedback_received_by_CE = feedback_received_by_CE
            ticket.save()
            serializer = TicketSerializer(ticket, context={'request': request})
            send_message_to_frontend("Ticket Feedback Received By Worker", serializer.data)

            return JsonResponse({"status": "success", "code": 200, "message": "Ticket Feedback Received By CE Updated Successfully"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "code": 400})
