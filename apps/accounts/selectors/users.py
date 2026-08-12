from apps.accounts.models import User, ProfessionalProfile, Profile

class UserSelector:
    @staticmethod
    def get_user_by_email(email: str) -> User:
        return User.active_objects.filter(email=email).first()

    @staticmethod
    def search_users(query):
        return User.active_objects.filter(email__icontains=query)

    @staticmethod
    def filter_users(**kwargs):
        return User.active_objects.filter(**kwargs)
