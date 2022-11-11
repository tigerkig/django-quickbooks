from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, username, password, **extra_fields):

        extra_fields.setdefault("admin", True)
        if extra_fields.get("admin") is not True:
            raise ValueError("Superuser must have admin=True.")
        
        """
        Do Extra Settings
        """

        return self.create_user(username, password, **extra_fields)