import random

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import Manager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)  # noqa
        username = GlobalUserModel.normalize_username(username)  # noqa
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)  # noqa
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class UserArgumentNotFound(Exception):
    pass


class OTPManager(Manager):
    def create(self, **kwargs):
        # Add custom logic before creating the object
        # For example, you can set default values or perform additional validations
        kwargs.update({'number': random.randint(100000, 999999)})
        # Call the original create method to create the object
        obj = self.model(**kwargs)
        obj.save(using=self._db)

        return obj

    def validate_otp(self, user, otp):
        otp_obj = self.filter(user=user, number=otp).first()

        if otp_obj:
            otp_obj.delete()
            return True
        return False

    def regenerate_otp(self, **kwargs):
        user = kwargs.get("user")
        user_id = kwargs.get("user_id")
        if user:
            self.filter(user=user).delete()
        elif user_id:
            self.filter(user_id=user_id).delete()
        else:
            raise UserArgumentNotFound("Write argument `user` or `user_id`")
        return self.create(**kwargs)
