from apps.core.utils import send_email
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  #
from datetime import timedelta
from django.db.models import Q
from .models import User
from .forms import (
    EditUserForm,
    EditUserProfileForm,
    EditUserEmailForm,
    UserPasswordSetupForm,
)
import time


UserModel = get_user_model()


@login_required
def personal_information(request):
    user = request.user
    context = {
        "user": user,
        "menu": "personal_information",
    }
    return render(request, "accounts/personal_information.html", context)


@login_required
def edit_personal_information(request):
    user = request.user
    if request.method == "POST":
        form = EditUserForm(instance=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("personal_information"))
    else:
        form = EditUserForm(instance=user)
    context = {
        "form": form,
        "menu": "personal_information",
    }
    return render(request, "accounts/edit_personal_information.html", context)


@login_required
def edit_personal_email(request):
    user = request.user
    if request.method == "POST":
        form = EditUserEmailForm(instance=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email_confirmation = False
            user.save()
            template_name = "accounts/acc_change_email.html"
            send_email(request, form, user, template_name)
            time.sleep(60)
            return render(request, "index.html")
    else:
        form = EditUserEmailForm(instance=user)
    context = {
        "form": form,
        "menu": "personal_information",
    }
    return render(request, "accounts/edit_email.html", context)


def login_view(request, template_name="accounts/login.html"):
    from .forms import UserAuthForm

    redirect_to = request.POST.get("next", request.GET.get("next", ""))
    do_redirect = False

    if request.user.is_authenticated:
        if redirect_to == request.path:
            raise ValueError("Redirection loop for authenticated user detected.")
        return redirect(reverse("index"))
    elif request.method == "POST":
        form = UserAuthForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse("index"))
    else:
        form = UserAuthForm(request)

    context = {
        "form": form,
    }
    return render(request, "accounts/login.html", context)


def redirect_to_popup(request):
    return render(request, "accounts/confirm_email.html", {})


def register(request, template_name="accounts/register.html"):
    from .forms import UserRegistrationForm
    from django.contrib.auth import login

    if request.user.is_authenticated:
        return redirect(reverse("index"))

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email_confirmation = False
            user.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            template_name = "accounts/acc_active_email.html"
            send_email(request, form, user, template_name)
            # time.sleep(60)
            # return render(request, 'accounts/confirm_email.html')
            return redirect(reverse("redirect_to_popup"))
    else:
        form = UserRegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.email_confirmation = True
        user.save()
        return render(request, "accounts/activate_mail.html")
    else:
        return render(request, "accounts/activate_error_messege.html")


def logout_view(request):
    _next = request.GET.get("next")
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)


@login_required
def set_password_for_linkedin_user(request):
    user = request.user
    if not user.has_usable_password():
        if request.method == "POST":
            form = UserPasswordSetupForm(request.POST or None, user=user)
            if form.is_valid():
                form.save()
                return redirect(reverse("personal_information"))
        else:
            form = UserPasswordSetupForm(request.POST or None, user=user)
        context = {
            "form": form,
            "menu": "personal_information",
        }
        return render(request, "accounts/edit_personal_information.html", context)
    else:
        return redirect(reverse("password_change"))


def request_password_reset(request):
    from apps.core.utils import send_email_reset_password
    from .forms import Password_ResetForm

    if request.method == "POST":
        form = Password_ResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    template_name = "accounts/email/password_reset.html"
                    send_email_reset_password(request, form, user, template_name)
                    return redirect("/password-reset/done/")
    form = Password_ResetForm()
    return render(
        request=request,
        template_name="accounts/password_reset.html",
        context={"form": form,},
    )
