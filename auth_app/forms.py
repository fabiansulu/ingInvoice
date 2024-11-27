from django import forms
from django.contrib.auth.models import User
from .models import *
from django.forms import TextInput, EmailInput, PasswordInput

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width:300px;',
                'placeholder':'Identifiant'
            }),
            'password' : PasswordInput(attrs={
                'class': 'form-control',
                'style': 'max-width:300px;',
                'placeholder':'Mot de passe'
            })
        }
        

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmer Mot de passe', widget=forms.PasswordInput)
   
    class Meta:
        model = User
        fields = ('username', 'first_name','last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd ['password2']:
            raise forms.ValidationError('Les Mots de passe ne correspondent pas.')
        return cd['password2']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class CompanyForm(forms.ModelForm):
    company_name = forms.CharField(label='Dénomination')
    company_email = forms.CharField(label='E-mail')
    company_address = forms.CharField(label='Adresse physique')
    #company_country = models.CharField(max_length=200, null=True, choices=CountryField().choices + [('', 'Selectionner un pays')])
    company_iban = forms.CharField(label='Compte bancaire et Iban', required=False)
    company_id = forms.CharField(label='Numéro d\'identification', required=False)
    company_logo = forms.ImageField(widget= forms.FileInput(attrs={'class':'form-control', 'rows':5}) ,label='Logo', required=False) 
    
    class Meta:
        model = Company_Profile
        fields = ['company_name','company_email', 'company_address','company_country','company_iban', 'company_id', 'company_logo' ] 
    
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)

        self.fields['company_name'].widget.attrs['class'] = 'form-control'
        self.fields['company_email'].widget.attrs['class'] = 'form-control'
        self.fields['company_address'].widget.attrs['class'] = 'form-control'
        self.fields['company_country'].widget.attrs['class'] = 'form-control'
        self.fields['company_iban'].widget.attrs['class'] = 'form-control'
        self.fields['company_id'].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm) : 
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.TextInput(attrs={
            'class':'form-control',
        })
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
        })
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'class':'form-control',
        })
        self.fields['email'].widget = forms.TextInput(attrs={
            'class':'form-control',
        })
