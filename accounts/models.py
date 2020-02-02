from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """部署モデル"""

    class Meta:
        db_table = 'department'
        verbose_name = verbose_name_plural = '部署'

    name = models.CharField('部署名', max_length=255)

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    """従業員モデル"""

    class Meta:
        db_table = 'employee'
        verbose_name = verbose_name_plural = '従業員'

    department = models.ForeignKey(Department, verbose_name='部署', on_delete=models.SET_NULL,
                                   null=True, blank=True)

    def __str__(self):
        return self.username
