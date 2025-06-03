from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

class Company_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.TextField( max_length=200, blank=False, null= False, default= 'My company')
    company_email = models.EmailField()
    company_address = models.TextField( max_length=200, blank=True)
    company_country = models.CharField(max_length=200, null=True) #choices= list(CountryField().choices) + [('', 'Selectionner un pays')]
    company_iban = models.TextField( max_length=50, blank=True)
    company_id = models.TextField( max_length=50, blank=True )
    company_logo = models.ImageField(default='default.svg', upload_to='company_logo/')

    #class meta:
     #   abstract = True
    
    def __str__(self):
        return "Company profile of {0}".format(self.user.username)

@receiver(post_save, sender=User)
def create_company_profile(sender, instance, created, **kwargs):
    if created:
        Company_Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_company_profile(sender, instance, **kwargs):
    try:
        instance.company_profile.save()

    except ObjectDoesNotExist:
        Company_Profile.objects.create(user=instance)
    



