from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _


class User(AbstractUser):
    pass


class SubUser(models.Model):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    username = models.CharField(
        _("username"),
        max_length=30,
        db_index=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, numbers and "
            "@/./+/-/_ characters"
        ),
    )
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_("e-mail address"), blank=True)
    password = models.CharField(_("password"), max_length=128)
    is_staff = False
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    is_superuser = False
    can_publish = models.BooleanField(default=False)
    can_pack = models.BooleanField(default=False)
    last_login = models.DateTimeField(_("last login"), default=timezone.now)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    owner = models.ForeignKey(User, related_name="subusers", on_delete=models.CASCADE)
