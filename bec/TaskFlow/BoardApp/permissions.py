from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Membership


class BoardPermission(BasePermission):
    message = "Недостаточно прав для этого действия."

    def has_object_permission(self, request, view, obj):
        role = (
            Membership.objects
            .filter(board=obj, user=request.user)
            .values_list("role", flat=True)
            .first()
        )

        if role is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method in ("POST", "PUT", "PATCH"):
            return role in (
                Membership.Role.MODERATOR,
                Membership.Role.OWNER,
            )

        if request.method == "DELETE":
            return role == Membership.Role.OWNER

        return False
