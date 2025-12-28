from .models import BlacklistedAccessToken

def CheckAccessToken(access_token):
    if BlacklistedAccessToken.objects.filter(token=access_token).exists():
        return True
    else:
        return False