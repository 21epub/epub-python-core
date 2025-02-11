class EpubPermissionService:
    @staticmethod
    def get_view_perm(request, view):
        view_permission_dict = getattr(view, "permissions", {})
        if not view_permission_dict:
            return
        view_perm = view_permission_dict.get(request.method)
        book_type = view.kwargs.get("book_type", "")
        if view_permission_dict.get("METHOD") == "DIRECTLY":
            return view_perm
        else:
            return ".".join([book_type, view_perm])
