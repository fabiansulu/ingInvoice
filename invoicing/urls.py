from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
path('',views.index, name='index'),
path('main_dashboard',views.main_dashboard, name='main_dashboard'),
path('invoices',views.invoices, name='invoices'),
path('products',views.products, name='products'),
path('clients',views.clients, name='clients'),

#Create URL Paths
path('invoices/create',views.createInvoice, name='create-invoice'),
path('invoices/create-build/<slug:slug>',views.createBuildInvoice, name='create-build-invoice'),

#Delete an invoice
path('invoices/delete/<slug:slug>',views.deleteInvoice, name='delete-invoice'),

#PDF and EMAIL Paths
path('invoices/view-pdf/<slug:slug>',views.viewPDFInvoice, name='view-pdf-invoice'),
#path('invoices/view-document/<slug:slug>',views.viewDocumentInvoice, name='view-document-invoice'),
#path('invoices/email-document/<slug:slug>',views.emailDocumentInvoice, name='email-document-invoice'),

#reportlab pdf
path('invoices/invoice_pdf/<slug:slug>', views.invoice_pdf, name='invoice_pdf'),
#path('invoices/pdf/<slug:slug>', views.pdf, name='pdf'),

#Company Settings Page
#path('company/settings',views.companySettings, name='company-settings'),

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
