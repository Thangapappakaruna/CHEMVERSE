from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from chemistry_games.models import GameScore
from chemistry_learning.models import LessonProgress
from chemistry_quiz.models import QuizResult
from community.models import Post
from compound_search.models import FavoriteCompound
from dashboard.models import Activity
from dashboard.utils import achievements
from molecular_structure.models import Structure
from reaction_builder.models import Reaction

from .forms import AccountEmailForm, LoginForm, ProfileForm, RegisterForm
from .models import Profile
from .utils import get_profile, read_verification_token, send_verification_email

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='accounts.backends.UsernameOrEmailBackend')
        try:
            send_verification_email(request, user)
            messages.success(request, f'Welcome, {user.username}! We sent a verification link to {user.email}.')
        except Exception:
            messages.warning(request, 'Account created, but the verification email could not be sent. Use "Resend" on your profile.')
        return redirect('dashboard:dashboard')
    return render(request, 'accounts/register.html', {'form': form})


class ChemLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)  # expires when the browser closes
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('dashboard:home')


def verify_email(request, token):
    try:
        uid, email = read_verification_token(token)
    except signing.SignatureExpired:
        messages.error(request, 'This verification link has expired. Request a new one from your profile.')
        return redirect('accounts:login')
    except signing.BadSignature:
        messages.error(request, 'Invalid verification link.')
        return redirect('dashboard:home')
    user = User.objects.filter(pk=uid, email__iexact=email).first()
    if not user:
        messages.error(request, 'This link no longer matches an account email.')
        return redirect('dashboard:home')
    Profile.objects.filter(user=user).update(email_verified=True)
    messages.success(request, 'Your email address is verified. Thank you!')
    return redirect('dashboard:dashboard' if request.user.is_authenticated else 'accounts:login')


@login_required
@require_POST
def resend_verification(request):
    if get_profile(request.user).email_verified:
        messages.info(request, 'Your email is already verified.')
    else:
        try:
            send_verification_email(request, request.user)
            messages.success(request, f'A new verification link was sent to {request.user.email}.')
        except Exception:
            messages.error(request, 'Could not send the email right now. Please try again later.')
    return redirect(request.POST.get('next') or 'accounts:profile_edit')


def profile(request, username):
    owner = get_object_or_404(User, username=username)
    prof = get_profile(owner)
    stats = {
        'lessons': LessonProgress.objects.filter(user=owner).count(),
        'quizzes': QuizResult.objects.filter(user=owner).count(),
        'games': GameScore.objects.filter(user=owner).count(),
        'structures': Structure.objects.filter(user=owner).count(),
        'reactions': Reaction.objects.filter(user=owner).count(),
        'posts': Post.objects.filter(author=owner).count(),
    }
    return render(request, 'accounts/profile.html', {
        'owner': owner, 'prof': prof, 'stats': stats, 'badges': achievements(owner),
        'public_structures': Structure.objects.filter(user=owner, is_public=True)[:6],
        'public_reactions': Reaction.objects.filter(user=owner, is_public=True)[:6],
        'is_me': request.user == owner})


@login_required
def my_profile(request):
    return redirect('accounts:profile', username=request.user.username)


@login_required
def profile_edit(request):
    prof = get_profile(request.user)
    pform = ProfileForm(request.POST or None, instance=prof, prefix='p')
    eform = AccountEmailForm(request.POST or None, instance=request.user, prefix='e')
    if request.method == 'POST' and pform.is_valid() and eform.is_valid():
        email_changed = 'email' in eform.changed_data
        pform.save()
        eform.save()
        if email_changed:
            Profile.objects.filter(pk=prof.pk).update(email_verified=False)
            try:
                send_verification_email(request, request.user)
                messages.info(request, 'Email changed – please verify the new address.')
            except Exception:
                messages.warning(request, 'Email changed, but the verification email could not be sent.')
        messages.success(request, 'Profile updated.')
        return redirect('accounts:my_profile')
    return render(request, 'accounts/profile_edit.html', {'pform': pform, 'eform': eform, 'prof': prof})


@login_required
def history(request):
    kind = request.GET.get('kind', '')
    qs = Activity.objects.filter(user=request.user)
    if kind:
        qs = qs.filter(kind=kind)
    page = Paginator(qs, 25).get_page(request.GET.get('page'))
    return render(request, 'accounts/history.html', {'page': page, 'kind': kind,
                                                     'kinds': Activity._meta.get_field('kind').choices})


@login_required
def saved(request):
    return render(request, 'accounts/saved.html', {
        'favorites': FavoriteCompound.objects.filter(user=request.user).select_related('compound'),
        'structures': Structure.objects.filter(user=request.user),
        'reactions': Reaction.objects.filter(user=request.user),
    })


class ResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/emails/password_reset_email.txt'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class ResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class ChangePasswordView(auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:my_profile')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for f in form.fields.values():
            f.widget.attrs['class'] = 'form-control'
        return form
