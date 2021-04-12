from django.db import models

# Create your models here.
class Contact(models.Model):
	"""Подписка на email"""
	email =models.EmailField("Email",)
	date = models.DateTimeField("Дата отправки",auto_now_add=True)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name='Контакт'
		verbose_name_plural='Контакты'	