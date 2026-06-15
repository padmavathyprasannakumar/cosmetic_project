from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "mobile",
            "address",
            "city",
            "state",
            "pin_code",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "e.g Narmatha",
                "class": "form-control"
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "e.g Thamaraj",
                "class": "form-control"
            }),
            "mobile": forms.TextInput(attrs={
                "placeholder": "Enter mobile number",
                "class": "form-control"
            }),
            "address": forms.TextInput(attrs={
                "placeholder": "123 Luxury Lane, Tenkasi",
                "class": "form-control"
            }),
            "city": forms.TextInput(attrs={
                "placeholder": "e.g Tenkasi",
                "class": "form-control"
            }),
            "state": forms.TextInput(attrs={
                "placeholder": "e.g Tamil Nadu",
                "class": "form-control"
            }),
            "pin_code": forms.TextInput(attrs={
                "placeholder": "Enter Pincode",
                "class": "form-control"
            }),
        }
