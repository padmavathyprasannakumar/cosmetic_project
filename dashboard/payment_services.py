import requests
from django.conf import settings

def cashfree_headers():
    return {
        "Content-Type": "application/json",
        "x-api-version": settings.CASHFREE_API_VERSION,
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
    }

def create_cashfree_order(payload):
    """
    Create a Cashfree order and return the response JSON
    """
    url = f"{settings.CASHFREE_BASE_URL}/orders"
    response = requests.post(url, headers=cashfree_headers(), json=payload, timeout=30)
    return response.json()