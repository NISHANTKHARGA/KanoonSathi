from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('lawyer', 'Lawyer'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username
    
class Lawyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='lawyer_appointments')

    date = models.DateField()
    time = models.TimeField()
    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('rejected', 'Rejected'),
]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.client.username} -> {self.lawyer.user.username}"