from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Membership


class BoardPermission(BasePermission):
    message = "У вас не достаточно прав"

    def has_object_permission(self, request, view, obj):
        user_permissions = (
            Membership.objects
            .filter(
            user=request.user, board=obj
            )
            .values_list("role", flat=True)
            .first()
        )

        if user_permissions is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method in ("POST", "PUT", "PATCH"):
            return user_permissions in (
                Membership.Role.OWNER,
                Membership.Role.MODERATOR,
            )
        
        if request.method == "DELETE":
            return user_permissions == Membership.Role.OWNER

        return False

