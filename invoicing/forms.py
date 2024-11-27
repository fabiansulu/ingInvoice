from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from .models import *
import json

#Form Layout from Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class DateInput(forms.DateInput):
    input_type = 'date'


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 'phoneNumber', 'emailAddress', 'taxNumber']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'quantity', 'price', 'currency']


class InvoiceForm(forms.ModelForm):
    THE_OPTIONS = [
    ('14 jours', '14 jours'),
    ('30 jours', '30 jours'),
    ('60 jours', '60 jours'),
    ]
    STATUS_OPTIONS = [
    ('ACTUELLE', 'ACTUELLE'),
    ('RETARD DE PYT', 'RETARD DE PYT'),
    ('PAYE', 'PAYE'),
    ]

    title = forms.CharField(
                    required = True,
                    label='Désignation de la Facture',
                    widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Entrer une désignation'}),)
    paymentTerms = forms.ChoiceField(
                    choices = THE_OPTIONS,
                    required = True,
                    label='Sélectionner un délai de paiment',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    status = forms.ChoiceField(
                    choices = STATUS_OPTIONS,
                    required = True,
                    label='Changer l\'etat de la Facture',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    notes = forms.CharField(
                    required = True,
                    label='Entrer une note pour le client',
                    widget=forms.Textarea(attrs={'class': 'form-control mb-3'}))

    dueDate = forms.DateField(
                        required = True,
                        label='Echéance de Facture',
                        widget=DateInput(attrs={'class': 'form-control mb-3'}),)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-6'),
                Column('dueDate', css_class='form-group col-md-6'),
                css_class='form-row'),
            Row(
                Column('paymentTerms', css_class='form-group col-md-6'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'),
            'notes',

            Submit('submit', ' MODIFIER FACTURE '))

    class Meta:
        model = Invoice
        fields = ['title', 'dueDate', 'paymentTerms', 'status', 'notes']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 'phoneNumber', 'emailAddress', 'taxNumber']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['clientName'].widget = forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Nom',
        })
        self.fields['clientLogo'].widget = forms.FileInput(attrs={
            'class': 'form-control-file',
        })
        self.fields['addressLine1'].widget = forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Adresse',
        })




class ProdSelectForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.initial_prod = kwargs.pop('initial_prod')
        self.PROD_LIST = Product.objects.all()
        self.PROD_CHOICES = [('-----', '--Sélectionner un produit--')]


        for product in self.PROD_LIST:
            d_t = (product.uniqueId, product.title)
            self.PROD_CHOICES.append(d_t)


        super(ProdSelectForm,self).__init__(*args,**kwargs)

        self.fields['title'] = forms.ChoiceField(
                                        label='Choisir un produit existant',
                                        choices = self.PROD_CHOICES,
                                        widget=forms.Select(attrs={'class': 'form-control mb-3'}),)

    class Meta:
        model = Product
        fields = ['title']

 
    def clean_prod(self):
        c_prod = self.cleaned_data['title']
        if c_prod == '-----':
            return self.initial_prod
        else:
            return Client.objects.get(uniqueId=c_prod)

class ClientSelectForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.initial_client = kwargs.pop('initial_client')
        self.CLIENT_LIST = Client.objects.all()
        self.CLIENT_CHOICES = [('-----', '--Sélectionner un client--')]


        for client in self.CLIENT_LIST:
            d_t = (client.uniqueId, client.clientName)
            self.CLIENT_CHOICES.append(d_t)


        super(ClientSelectForm,self).__init__(*args,**kwargs)

        self.fields['client'] = forms.ChoiceField(
                                        label='Choisir un client relatif',
                                        choices = self.CLIENT_CHOICES,
                                        widget=forms.Select(attrs={'class': 'form-control mb-3'}),)

    class Meta:
        model = Invoice
        fields = ['client']


    def clean_client(self):
        c_client = self.cleaned_data['client']
        if c_client == '-----':
            return self.initial_client
        else:
            return Client.objects.get(uniqueId=c_client)


#Settings form

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['clientName', 'addressLine1', 'province',
                  'postalCode', 'phoneNumber', 'emailAddress',
                  'taxNumber', 'clientLogo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['clientName'].widget = forms.TextInput(attrs={
            'class':'form-control',
        })
        self.fields['clientLogo'].widget = forms.FileInput(attrs={
            'class': 'form-control-file',
        })
        self.fields['addressLine1'].widget = forms.TextInput(attrs={
            'class':'form-control',
        })


















# <input type="email" class="form-control" id="floatingInput" placeholder="name@example.com">
# <input type="password" class="form-control" id="floatingPassword" placeholder="Password">