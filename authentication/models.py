from django.db import models
from django.contrib.auth.models import AbstractUser 
from PIL import Image
from django.conf import settings
from djstripe.models import Customer

class User(AbstractUser):
    GENDER_CHOICES = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics/', null=True, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1)

    def __str__(self):
        return f'{self.username}'

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    @property
    def customer(self):
        try:
          customer = Customer.objects.get(subscriber=self)
          return customer
        except:
          return None

    @property
    def get_active_subscriptions(self):
        try:
          customer = Customer.objects.get(subscriber=self)
          return customer.active_subscriptions
        except:
          return []

    @property
    def get_active_plan(self):
        try:
          customer = Customer.objects.get(subscriber=self)
          return customer.active_subscriptions[0].plan
        except:
          return None

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_image_url(self):
        try:
            if self.image:
                return self.image.url
            return f"{settings.MEDIA_URL}/no_image.jpg"
        except:
            return ""