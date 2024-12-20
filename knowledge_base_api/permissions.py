from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

  def has_permission(self, request, view):
    User = get_user_model()
    return super().has_permission(request, view)