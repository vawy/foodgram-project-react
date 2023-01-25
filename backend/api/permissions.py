from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AuthorStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method == 'GET'
            or (request.user == obj.author)
            or request.user.is_staff
        )
