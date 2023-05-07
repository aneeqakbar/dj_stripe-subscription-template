from django.urls import path
from . import views


urlpatterns = [
    path("create-session/", views.CreateCheckoutSession.as_view(), name="CreateCheckoutSession"),
    path("success/", views.SuccessView.as_view(), name="SuccessView"),
    path("cancelled/", views.CancelView.as_view(), name="CancelView"),
    path("cancel-subscription/", views.CancelSubscriptionView.as_view(), name="CancelSubscriptionView"),
    path("change-subscription/", views.ChangeSubscriptionView.as_view(), name="ChangeSubscriptionView"),
    path("invoices/", views.ListInvoiceView.as_view(), name="ListInvoiceView"),
]
