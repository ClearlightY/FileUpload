from django.db import models


# Create your models here.
class upload_info(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField()
    path = models.CharField(max_length=255)
    md5 = models.CharField(max_length=33, default='')
    size = models.CharField(max_length=30, default=0)


class check_info(models.Model):
    uuid = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    check_date = models.DateTimeField()
    path = models.CharField(max_length=255)
