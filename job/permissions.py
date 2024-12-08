from rest_framework.permissions import BasePermission

class IsJobPoster(BasePermission):
    """
    Custom permission to allow only users in the 'job_posters' group or 
    Admins to create job postings.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user belongs to the group 'job_posters' or is a superuser
        return (
            request.user.groups.filter(name='job_posters').exists() or 
            request.user.is_superuser
        )
