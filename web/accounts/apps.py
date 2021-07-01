from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        from accounts.receivers import update_login_info

        user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")
        user_logged_in.connect(update_login_info, dispatch_uid="update_last_login")
