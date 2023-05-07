from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import UserRegisterForm, UserUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from djstripe.models import Plan

class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.get_active_subscriptions:
            return redirect("users:ProfileView")
        plans = Plan.objects.filter(active=True)
        context = {
          "plans": plans
        }
        return render(request, "home.html", context)

class RegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})

    def  post(self, request):
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, f'Your account has been created! Please complete payment to activate account')
            request.session["user_id"] = user.id
            request.session["plan_id"] = request.COOKIES.get("selectedPlan")
            return redirect('CreateCheckoutSession')
        return render(request, 'users/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):

        u_form = UserUpdateForm(instance=request.user)

        context = {
            'u_form': u_form
        }

        return render(request, 'users/profile.html', context)

    def post(self, request):
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('users:ProfileView')
        context = {
            'u_form': u_form
        }
        return render(request, 'users/profile.html', context)

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/change_password.html"

    def get_success_url(self):
        return reverse("users:HomeView")
