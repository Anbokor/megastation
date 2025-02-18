from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle

class LoginAttemptThrottle(SimpleRateThrottle):
    """
    ✅ Ограничивает частоту попыток входа для анонимных пользователей.
    """
    scope = "login_attempt"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None  # Аутентифицированные пользователи не ограничиваются
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}

class LoginAttemptUserThrottle(ScopedRateThrottle):
    """
    ✅ Ограничение попыток входа для зарегистрированных пользователей
    """
    scope = "login_attempt_user"
