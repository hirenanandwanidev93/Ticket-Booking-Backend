from api.authentication.viewsets import (
    RegisterViewSet,
    LoginViewSet,
    ActiveSessionViewSet,
    LogoutViewSet,
)
from api.ticketRelay.views import (
    TicketViewSet,
    addNewTicketViewSet,
    addManagerFeedbackViewSet,
    addNewPushUser,
    TicketInQueueViewSet,
    TicketCompletedActionViewSet,
    dashboardInformations,
    addWorkerFeedbackViewSet,
    timerTimeOut,
    GetExpiredTicketsViewSet,
    download_latest_CE,
    latest_CE_version_available,
    download_CE,
    VerifyApiKeys,
    NewTicketPage,
    confirmFeedbackReceivalViewSet,
    GetExpiredTicketsByActualDateViewSet,
    TicketCompletedByActualDateActionViewSet
)
from rest_framework import routers
from api.user.viewsets import UserViewSet
from django.urls import path

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"edit", UserViewSet, basename="user-edit")

router.register(r"register", RegisterViewSet, basename="register")

router.register(r"getAllTickets", TicketViewSet, basename="getAllTickets")

router.register(r"NewTicketPage", NewTicketPage, basename="NewTicketPage")

router.register(r"VerifyApiKeys", VerifyApiKeys, basename="VerifyApiKeys")

router.register(r"getDashboardInfo", dashboardInformations,
                basename="getDashboardInfo")

router.register(r"getQueuedTickets", TicketInQueueViewSet,
                basename="getAllTickets")

router.register(r"getConfirmedTickets",
                TicketCompletedActionViewSet, basename="getCompletedTickets")

router.register(r"getConfirmedTicketsByActualDate",
                TicketCompletedByActualDateActionViewSet, basename="TicketCompletedByActualDateAction")

router.register(r"getExpiredTickets",
                GetExpiredTicketsViewSet, basename="getExpiredTickets")

router.register(r"getExpiredTicketsByActualDate",
                GetExpiredTicketsByActualDateViewSet, basename="GetExpiredTicketsByActualDate")

router.register(r"latest_CE_version_available",
                latest_CE_version_available, basename="latest_CE_version_available")
 
router.register(r"download_CE",
                download_CE, basename="download_CE")

router.register(r"addNewTicket", addNewTicketViewSet, basename="addNewTicket")

router.register(r"addNewPushUser", addNewPushUser, basename="addNewPushUser")

router.register(r"addManagerFeedback",
                addManagerFeedbackViewSet, basename="addNewTicket")

router.register(r"addWorkerFeedback", addWorkerFeedbackViewSet,
                basename="addWorkerFeedback")

router.register(r"timerTimeOut", timerTimeOut,
                basename="timerTimeOut")

router.register(r"login", LoginViewSet, basename="login")

router.register(r"checkSession", ActiveSessionViewSet,
                basename="check-session")

router.register(r"logout", LogoutViewSet, basename="logout")

router.register(r"confirmFeedbackReceive", confirmFeedbackReceivalViewSet, basename="confirmFeedbackReceive")


urlpatterns = [
    *router.urls,
    path('download_latest_CE/', download_latest_CE.as_view()),
]
