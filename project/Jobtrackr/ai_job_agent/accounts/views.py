import random
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model, login
from .forms import CustomUserCreationForm, UserProfileForm
from .models import OTPVerification

User = get_user_model()

def send_otp_email(user, otp_code):
    """
    Sends verification OTP to user's registered email.
    """
    subject = "[AI Job Agent] Email Verification OTP"
    message = f"Hello {user.username},\n\nYour 6-digit verification code is: {otp_code}\n\nThis OTP is valid for 10 minutes. Please enter this code on the verification page to activate your profile.\n\nBest,\nAI Job Agent Team"
    email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'verification@jobtrackr.ai')
    recipient_list = [user.email]
    
    send_mail(
        subject=subject,
        message=message,
        from_email=email_from,
        recipient_list=recipient_list,
        fail_silently=True
    )

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save user, but set inactive until OTP email verification
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        # Generate 6-digit code
        otp_code = str(random.randint(100000, 999999))
        
        # Store in verification db
        OTPVerification.objects.create(
            user=user,
            code=otp_code,
            purpose='register'
        )
        
        # Send mail
        send_otp_email(user, otp_code)
        
        messages.success(self.request, "Account registered! A 6-digit OTP code has been sent to your email. Please verify below.")
        return redirect(f"/accounts/verify-otp/?username={user.username}")


class VerifyOTPView(View):
    """
    Handles OTP entry verification page.
    """
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        user = get_object_or_404(User, username=username)
        return render(request, 'accounts/verify_otp.html', {'username': username, 'user_email': user.email})

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        otp_entered = request.POST.get('otp_code', '').strip()
        
        user = get_object_or_404(User, username=username)
        
        # Find matches
        otp_record = OTPVerification.objects.filter(user=user, purpose='register').first()
        
        if otp_record:
            if otp_record.is_expired:
                messages.error(request, "The OTP has expired. Please request a new code.")
                return render(request, 'accounts/verify_otp.html', {'username': username, 'user_email': user.email})
                
            if otp_record.code == otp_entered:
                # Success! Activate user profile
                user.is_active = True
                user.is_email_verified = True
                user.save()
                
                # Clear used codes
                OTPVerification.objects.filter(user=user).delete()
                
                # Login automatically
                login(request, user)
                
                messages.success(request, f"Welcome {user.username}! Your email has been verified successfully.")
                return redirect('core:index')
            else:
                messages.error(request, "Incorrect OTP code. Please try again.")
        else:
            messages.error(request, "No verification process found for this user.")
            
        return render(request, 'accounts/verify_otp.html', {'username': username, 'user_email': user.email})


class ResendOTPView(View):
    """
    Allows resending verification codes.
    """
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        user = get_object_or_404(User, username=username)
        
        # Clear existing verification records
        OTPVerification.objects.filter(user=user).delete()
        
        # Generate new
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            user=user,
            code=otp_code,
            purpose='register'
        )
        
        # Send
        send_otp_email(user, otp_code)
        
        messages.success(request, "A fresh 6-digit OTP code has been dispatched to your email.")
        return redirect(f"/accounts/verify-otp/?username={user.username}")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = "Profile updated successfully!"

    def get_object(self, queryset=None):
        return self.request.user
