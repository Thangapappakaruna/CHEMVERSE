from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class UsernameOrEmailBackend(ModelBackend):
    """Log in with either the User ID (username) or the email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        User = get_user_model()
        users = list(User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))[:2])
        if len(users) != 1:
            User().set_password(password)  # equalise timing
            return None
        user = users[0]
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
