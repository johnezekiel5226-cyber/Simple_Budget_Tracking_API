# budget_tracker/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow owners to edit, others may not access. For listing, viewsets will filter queryset to user's items.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow owners to access the object
        return obj.owner == request.user
