from rest_framework.authentication import BaseAuthentication


class User(object):
    """
    this is a virtual user, since real user from user store
    """

    is_authenticated = True

    def __init__(self, **kwargs):
        """
        {
          "username": "1-310",
          "updated": null,
          "sourceType": 1,
          "name": "",
          "created": null,
          "deleted": null,
          "phone": "",
          "id": 8,
          "subuser": {
            "username": "xiaoming",
            "updated": null,
            "created": null,
            "deleted": null,
            "avatar": null,
            "nickname": "小明"
          },
          "source": 0,
          "avatar": "http://cdn1.zhizhucms.com/avatars/anonymous.png",
          "accounting": null,
          "active": true,
          "attributes": null,
          "authentication_token": "rj2heIBIB5HtDXoSr3L6Ezkl0vDV7C",
          "email": "",
          "privilege": 1
        }
        :param kwargs:
        """
        self.id = kwargs.pop("id")
        self.username = kwargs.pop("username")

        self.subuser = kwargs.pop("subuser")
        if self.subuser:
            self.subuser_id = self.subuser.get("id")
            self.subuser_name = self.subuser.get("nickname", "")
            self.subuser_perms = self.subuser.get("perms", [])
            self.subuser_is_superuser = self.subuser.get("is_superuser", False)
        else:
            self.subuser_id = None
            self.subuser_name = None
            self.subuser_perms = []
            self.subuser_is_superuser = False

        self.is_superuser = False
        # logger.info("kwargs results: %s" % kwargs)

    def __str__(self):
        return f"{self.id} - {self.username} - {self.subuser_id} - {self.subuser_name}"


class MockUserAuthentication(BaseAuthentication):
    default_perms = [
        {"code": "cbt.list"},
        {"code": "cbt.create"},
        {"code": "h5.list"},
        {"code": "h5.create"},
        {"code": "h5.update"},
        {"code": "h5.delete"},
    ]
    add_perms = [
        {"code": "h5.list.show_all_user_contents"},
        {"code": "h5.update.show_all_user_contents"},
        {"code": "h5.delete.show_all_user_contents"},
        {"code": "admin.label.menu"},
    ]
    perms = default_perms + add_perms

    def authenticate(self, request):
        return (
            User(
                id=1,
                username="21epub",
                subuser={
                    "id": 1,
                    "nickname": "test1",
                    "is_superuser": False,
                    "perms": self.perms,
                },
            ),
            "token_xxxx",
        )
