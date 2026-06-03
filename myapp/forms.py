from django import forms
from .models import Product
from django.contrib.auth.models import User

ROLE_CHOICES = [('customer', 'Customer'), ('vendor', 'Vendor')]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'file', 'image']


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

    def check_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('password fields do not match')
        return self.cleaned_data['password2']


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    city = forms.CharField(max_length=50)
    payment_method = forms.ChoiceField(
        choices=[('bank_transfer', 'Bank Transfer'), ('cod', 'Cash on Delivery')],
        widget=forms.RadioSelect
    )
