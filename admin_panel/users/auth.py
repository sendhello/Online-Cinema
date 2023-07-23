import http
import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from .constants import Roles


User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'email': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))

        if response.status_code == http.HTTPStatus.OK:
            data = response.json()

            try:
                user, created = User.objects.get_or_create(id=data['id'])
                user.set_password(password)
                user.email = data.get('email')
                user.first_name = data.get('first_name')
                user.last_name = data.get('last_name')
                user.is_admin = data.get('role') == Roles.ADMIN
                user.is_staff = user.is_admin
                user.is_active = True
                user.save()

            except Exception:
                return None

            return user

        else:
            # Если не получилось получить данные по пользователю из внешней аутентификации,
            # пробуем взять данные из собственной БД
            try:
                user = User.objects.get(email=username)
                if user and user.check_password(password):
                    return user

            except Exception:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return None
