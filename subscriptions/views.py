from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.http.response import JsonResponse
from djstripe.models import Customer, Plan
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from djstripe import webhooks
from djstripe.models import Subscription
from django.contrib import messages
import stripe
import datetime

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

# Create your views here.

User = get_user_model()


class CreateCheckoutSession(View):
    def get(self, request):
        user_id = request.session.get("user_id")
        plan_id = request.session.get("plan_id")

        if not user_id and not plan_id and request.user.is_authenticated:
            user_id = request.user.id
            plan_id = request.COOKIES.get("selectedPlan")

        user = User.objects.get(id=user_id)

        customer = Customer.objects.filter(subscriber=user).first()

        if not customer:
            customer_data = stripe.Customer.create(email=user.email)
            customer = Customer.sync_from_stripe_data(customer_data)
            customer.subscriber = user
            customer.save()

        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            subscription_data={
                "items": [
                    {
                        "plan": plan_id,
                    }
                ],
                "metadata": {
                    "user_id": user.id,
                },
            },
            success_url="http://localhost:8000/subscriptions/success/",
            cancel_url="http://localhost:8000/subscriptions/cancelled/",
        )
        return redirect(session.url)


class CancelSubscriptionView(View):
    def get(self, request):
        if len(request.user.get_active_subscriptions) > 0:
            stripe.Subscription.delete(request.user.get_active_subscriptions[0].id)
            messages.success(request, "Subscription cancelled successfully")
        return redirect("users:ProfileView")


class ChangeSubscriptionView(View):
    def get(self, request):
        plans = Plan.objects.filter(active=True)
        context = {"plans": plans}
        return render(request, "subscriptions/change-subscription.html", context)

    def post(self, request):
        plan_id = request.POST.get("plan_id", None)
        plan = get_object_or_404(Plan, id=plan_id)

        active_subscriptions = request.user.get_active_subscriptions
        if len(active_subscriptions) > 0:
            subscription_id = active_subscriptions[0].id
            print(subscription_id)

            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
                proration_behavior="always_invoice",
                items=[
                    {
                        "plan": plan.id,
                    }
                ],
            )
            messages.success(
                request,
                "Subscription change request sent, It will be changed in a few minutes",
            )
            return redirect("users:ProfileView")
        messages.error(request, "Something went wrong")
        return redirect("users:ProfileView")

class ListInvoiceView(LoginRequiredMixin, View):
    def get(self, request):
        customer = request.user.customer
        if customer:
            invoices = stripe.Invoice.list(customer=customer.id)
            context = {
              "invoices": invoices
            }
            return render(request, "subscriptions/incoive_list.html", context)

class SuccessView(TemplateView):
    template_name = "subscriptions/success.html"


class CancelView(TemplateView):
    template_name = "subscriptions/cancel.html"


@webhooks.handler("payment_intent.succeeded")
def payment_intent_succeeded_event_listener(event, **kwargs):
    invoice_id = event.data["object"]["invoice"]

    invoice = stripe.Invoice.retrieve(invoice_id)
    lines = invoice.get("lines", [])

    if lines:
        user_id = lines["data"][0]["metadata"].get("user_id", None)
        user = User.objects.filter(id=user_id).first()
        if user:
            user.is_active = True
            user.save()
    return


@webhooks.handler("customer.subscription.updated")
def subscription_updated_event_listener(event, **kwargs):
    subscription_id = event.data["object"]["id"]
    plan_id = event.data["object"]["items"]["data"][-1]["plan"]["id"]
    subscription = Subscription.objects.get(id=subscription_id)
    plan = Plan.objects.get(id=plan_id)
    subscription.plan = plan
    subscription.save()
    return


@webhooks.handler("customer.subscription.deleted")
def subscription_cancelled_event_listener(event, **kwargs):
    subscription_id = event.data["object"]["id"]
    subscription = Subscription.objects.get(id=subscription_id)
    subscription.canceled_at = datetime.datetime.now()
    subscription.save()
    return


# stripe listen --forward-to localhost:8000/stripe/webhook/

