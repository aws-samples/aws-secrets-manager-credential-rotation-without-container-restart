from django import forms

class CustomerProfileForm(forms.Form):
    account_number=forms.CharField(label='Account Number', min_length=8,max_length=8)
    userid=forms.CharField(label='UserId', min_length=6,max_length=6)
