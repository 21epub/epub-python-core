def get_user_and_subuser_id_nickname(request):
    if request and request.user.is_authenticated:
        user_id = request.user.id
        subuser_id = request.user.subuser_id
        nickname = request.user.subuser_name

    else:
        subuser_id = None
        nickname = None
        user_id = None

    return user_id, subuser_id, nickname


class GetUserViewMixin:
    def get_user(self):
        request = self.request
        if request and request.user.is_authenticated:
            return request.user
        else:
            return None

    def get_user_subuser(self) -> (str, str, str):
        request = self.request
        if request:
            user_id, subuser_id, nickname = get_user_and_subuser_id_nickname(request)
            return user_id, subuser_id, nickname
        else:
            return None, None, None


class SetCreatorMixin:
    def get_user_subuser(self) -> (str, str, str):
        request = self.context.get("request")
        if request:
            user_id, subuser_id, nickname = get_user_and_subuser_id_nickname(request)
            return user_id, subuser_id, nickname
        else:
            return None, None, None

    def create(self, validated_data):
        user_id, subuser_id, nickname = self.get_user_subuser()
        validated_data["user_id"] = user_id
        validated_data["subuser_id"] = subuser_id
        validated_data["nickname"] = nickname
        return super().create(validated_data)
