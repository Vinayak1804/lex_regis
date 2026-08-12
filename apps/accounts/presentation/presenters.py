class AuthPresenter:
    @staticmethod
    def build_login_context(error_message=None):
        return {
            'error': error_message,
            'title': 'Sign In | Lex Regis',
        }
