from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':'Enter Password',
    'class':'form-control'
  }))
  
  confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':'confirm_password',
    'class':'form-control'
  }))
  
  class Meta:
    model = Account
    fields = ['first_name','last_name','email','phone_number','password']
    
    
  def __init__(self, *args, **kwargs):
      super(RegistrationForm, self).__init__(*args, **kwargs)
      self.fields['first_name'].widget.attrs.update({
          'placeholder': 'Enter First Name',
          'class': 'form-control'
      })
      self.fields['last_name'].widget.attrs.update({
          'placeholder': 'Enter Last Name',
          'class': 'form-control'
      })
      self.fields['phone_number'].widget.attrs.update({
          'placeholder': 'Enter Phone Number',
          'class': 'form-control'
      })
      self.fields['email'].widget.attrs.update({
          'placeholder': 'Enter Email Address',
          'class': 'form-control'
      })
      for field in self.fields:
        self.fields[field].widget.attrs.setdefault('class', 'form-control')

  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    if password != confirm_password:
      raise forms.ValidationError(
        "Password does not match!"
      )
      
    return cleaned_data 
    
    
  