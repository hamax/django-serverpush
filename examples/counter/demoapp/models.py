from django.db import models

class Data(models.Model):
	counter = models.IntegerField(default = 0)
