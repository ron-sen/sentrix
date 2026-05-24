
import secrets
from datetime import datetime ,  timedelta
def secret_token():

    return secrets.token_urlsafe(16)


def token_expiry():
    
    expiry_time = datetime.utcnow() + timedelta(hours=24)

    return expiry_time


