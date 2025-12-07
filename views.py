from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import IncidentReport, Notification, UserProfile
from .forms import CustomUserCreationForm, IncidentReportForm, IncidentStatusForm

class CustomLoginView(LoginView):
    template_name = 'emergency/login.html'
    
    def get_success_url(self):
        return self.get_redirect_url() or '/dashboard/'

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('emergency:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'emergency/guidelines.html', {'form': form})

@login_required
def dashboard_view(request):
    user_role = request.user.userprofile.role
    
    if user_role == 'fire':
        return redirect('emergency:fire_dashboard')
    elif user_role == 'health':
        return redirect('emergency:health_dashboard')
    elif user_role == 'social':
        return redirect('emergency:social_dashboard')
    elif user_role == 'admin':
        return redirect('emergency:admin_dashboard')
    else:  # student
        return redirect('emergency:student_dashboard')

@login_required
def student_dashboard(request):
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.save()
            messages.success(request, 'Incident reported successfully!')
            return redirect('emergency:student_dashboard')
    else:
        form = IncidentReportForm()
    
    my_incidents = IncidentReport.objects.filter(reporter=request.user)
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    context = {
        'form': form,
        'my_incidents': my_incidents,
        'notifications': notifications,
        'user_role': 'student'
    }
    return render(request, 'emergency/student_dashboard.html', context)

@login_required
def fire_dashboard(request):
    if request.user.userprofile.role != 'fire':
        messages.error(request, 'Access denied.')
        return redirect('emergency:dashboard')
    
    fire_incidents = IncidentReport.objects.filter(category='fire')
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    stats = {
        'reported': fire_incidents.count(),
        'in_progress': fire_incidents.filter(status='in_progress').count(),
        'resolved': fire_incidents.filter(status='resolved').count(),
        'total': fire_incidents.count(),
    }
    
    context = {
        'incidents': fire_incidents,
        'notifications': notifications,
        'stats': stats,
        'user_role': 'fire',
        'dashboard_title': 'Fire Department Dashboard'
    }
    return render(request, 'emergency/department_dashboard.html', context)

@login_required
def health_dashboard(request):
    if request.user.userprofile.role != 'health':
        messages.error(request, 'Access denied.')
        return redirect('emergency:dashboard')
    
    health_incidents = IncidentReport.objects.filter(category='health')
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    stats = {
        'reported': health_incidents.count(),
        'in_progress': health_incidents.filter(status='in_progress').count(),
        'resolved': health_incidents.filter(status='resolved').count(),
        'total': health_incidents.count(),
    }
    
    context = {
        'incidents': health_incidents,
        'notifications': notifications,
        'stats': stats,
        'user_role': 'health',
        'dashboard_title': 'Health Department Dashboard'
    }
    return render(request, 'emergency/department_dashboard.html', context)

@login_required
def social_dashboard(request):
    if request.user.userprofile.role != 'social':
        messages.error(request, 'Access denied.')
        return redirect('emergency:dashboard')
    
    social_incidents = IncidentReport.objects.filter(category='social')
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    stats = {
        'reported': social_incidents.count(),
        'in_progress': social_incidents.filter(status='in_progress').count(),
        'resolved': social_incidents.filter(status='resolved').count(),
        'total': social_incidents.count(),
    }
    
    context = {
        'incidents': social_incidents,
        'notifications': notifications,
        'stats': stats,
        'user_role': 'social',
        'dashboard_title': 'Social/Bullying Center Dashboard'
    }
    return render(request, 'emergency/department_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if request.user.userprofile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('emergency:dashboard')
    
    all_incidents = IncidentReport.objects.all()
    all_users = UserProfile.objects.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    stats = {
        'total_incidents': all_incidents.count(),
        'fire_incidents': all_incidents.filter(category='fire').count(),
        'health_incidents': all_incidents.filter(category='health').count(),
        'social_incidents': all_incidents.filter(category='social').count(),
        'reported_incidents': all_incidents.filter(status='reported').count(),
        'in_progress_incidents': all_incidents.filter(status='in_progress').count(),
        'resolved_incidents': all_incidents.filter(status='resolved').count(),
        'pending_incidents': all_incidents.filter(status__in=['reported', 'in_progress']).count(),
    }
    
    in_progress_incidents = all_incidents.filter(status='in_progress')
    print(f"DEBUG: In Progress incidents: {in_progress_incidents.count()}")
    for incident in in_progress_incidents:
        print(f"  - {incident.title} (ID: {incident.id}, Status: {incident.status})")
    
    context = {
        'incidents': all_incidents,
        'users': all_users,
        'notifications': notifications,
        'stats': stats,
        'user_role': 'admin'
    }
    return render(request, 'emergency/admin_dashboard.html', context)

@login_required
def update_incident_status(request, incident_id):
    incident = get_object_or_404(IncidentReport, id=incident_id)
    
    user_role = request.user.userprofile.role
    if user_role == 'admin' or (
        (user_role == 'fire' and incident.category == 'fire') or
        (user_role == 'health' and incident.category == 'health') or
        (user_role == 'social' and incident.category == 'social')
    ):
        if request.method == 'POST':
            form = IncidentStatusForm(request.POST, instance=incident)
            if form.is_valid():
                old_status = incident.status
                incident = form.save()
                
                if incident.reporter and old_status != incident.status:
                    Notification.objects.create(
                        user=incident.reporter,
                        message=f"Your incident '{incident.title}' status has been updated to {incident.get_status_display()}",
                        incident=incident
                    )
                
                messages.success(request, 'Incident status updated successfully!')
                return redirect(request.META.get('HTTP_REFERER', 'emergency:dashboard'))
    else:
        messages.error(request, 'You do not have permission to update this incident.')
    
    return redirect('emergency:dashboard')

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notification_data = []
    
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'notifications': notification_data,
        'count': notifications.count()
    })

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(IncidentReport, id=incident_id)
    
    user_role = request.user.userprofile.role
    can_view = (
        user_role == 'admin' or
        incident.reporter == request.user or
        (user_role == 'fire' and incident.category == 'fire') or
        (user_role == 'health' and incident.category == 'health') or
        (user_role == 'social' and incident.category == 'social')
    )
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this incident.')
        return redirect('emergency:dashboard')
    
    # Check if user can update status
    can_update = (
        user_role == 'admin' or
        (user_role == 'fire' and incident.category == 'fire') or
        (user_role == 'health' and incident.category == 'health') or
        (user_role == 'social' and incident.category == 'social')
    )
    
    status_form = IncidentStatusForm(instance=incident) if can_update else None
    
    context = {
        'incident': incident,
        'status_form': status_form,
        'can_update': can_update
    }
    return render(request, 'emergency/incident_detail.html', context)


@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('emergency:login')