from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a read-only for all users
    (even those not authenticated).
    """

    def has_permission(self, request, view):
        return bool(
            (request.method in SAFE_METHODS) or (request.user and request.user.is_staff)
        )
