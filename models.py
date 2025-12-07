from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("fire", "Fire Department"),
        ("health", "Health Department"), 
        ("social", "Social/Bullying Center"),
        ("admin", "Admin"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='student')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

class IncidentReport(models.Model):
    CATEGORY_CHOICES = [
        ("fire", "Fire"),
        ("health", "Health"),
        ("social", "Social/Bullying"),
        ("other", "Other"),
    ]
    
    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="reported")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='incidents/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


@receiver(post_save, sender=IncidentReport)
def create_incident_notification(sender, instance, created, **kwargs):
    if created:
        if instance.category == 'fire':
            fire_users = User.objects.filter(userprofile__role='fire')
            for user in fire_users:
                Notification.objects.create(
                    user=user,
                    message=f"New fire incident reported: {instance.title} at {instance.location}",
                    incident=instance
                )
        elif instance.category == 'health':
            health_users = User.objects.filter(userprofile__role='health')
            for user in health_users:
                Notification.objects.create(
                    user=user,
                    message=f"New health incident reported: {instance.title} at {instance.location}",
                    incident=instance
                )
        elif instance.category == 'social':
            social_users = User.objects.filter(userprofile__role='social')
            for user in social_users:
                Notification.objects.create(
                    user=user,
                    message=f"New social/bullying incident reported: {instance.title} at {instance.location}",
                    incident=instance
                )
        
        admin_users = User.objects.filter(userprofile__role='admin')
        for user in admin_users:
            Notification.objects.create(
                user=user,
                message=f"New incident reported: {instance.title} ({instance.get_category_display()}) at {instance.location}",
                incident=instance
            )
        
        if instance.reporter and not created:
            Notification.objects.create(
                user=instance.reporter,
                message=f"Your incident '{instance.title}' status has been updated to {instance.get_status_display()}",
                incident=instance
            )