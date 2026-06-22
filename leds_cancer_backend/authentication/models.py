from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class BaseUser(User):
    pass


class Doctor(BaseUser):
    crm = models.CharField(max_length=50, unique=True, null=False, blank=False)

    class Meta:
        verbose_name = "Doutor(a)"
        verbose_name_plural = "Doutores(as)"
        __table__ = "doctor"
