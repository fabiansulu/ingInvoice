from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import *
from .models import *
from .functions import *
from auth_app.forms import *
from django.contrib.auth.models import User, auth
from random import randint
from uuid import uuid4

from django.http import HttpResponse
from django.http import Http404
#import pdfkit
from django.template.loader import get_template
import os

#import for pdf generator using reportlab
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from .pdf import *

import locale
locale.setlocale(locale.LC_ALL,"")

from ingInvoice import renderers

def index(request):
    context = {}
    return render(request, 'invoice/index.html', context)


@login_required
def main_dashboard(request):
    clients = Client.objects.all().count()
    invoices = Invoice.objects.all().count()
    paidInvoices = Invoice.objects.filter(status='PAYE').count()


    context = {}
    context['clients'] = clients
    context['invoices'] = invoices
    context['paidInvoices'] = paidInvoices
    return render(request, 'invoice/main_dashboard.html', context)



@login_required
def invoices(request):
    context = {}
    invoices = Invoice.objects.all()
    context['invoices'] = invoices

    return render(request, 'invoice/invoices.html', context)


@login_required
def products(request):
    context = {}
    products = Product.objects.all()
    prod_form  = ProductForm()
    context['products'] = products
    context['prod_form'] = prod_form

    if request.method == 'POST':
        prod_form  = ProductForm(request.POST)
        
        if prod_form.is_valid():
            obj = prod_form.save(commit=False)
            obj.save()

            messages.success(request, "Produit ajouté avec succès")
            return redirect('products')
        
        else:
            context['prod_form'] = prod_form
            messages.error(request,"Un problème est survenu")
            return render(request, 'invoice/products.html', context)
        
    return render(request, 'invoice/products.html', context)



@login_required
def clients(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients

    if request.method == 'GET':
        form = ClientForm()
        context['form'] = form
        return render(request, 'invoice/clients.html', context)

    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, 'Nouveau client ajouté !')
            return redirect('clients')
        else:
            messages.error(request, 'Problem processing your request')
            return redirect('clients')


    return render(request, 'invoice/clients.html', context)



###--------------------------- Create Invoice Views Start here --------------------------------------------- ###

@login_required
def createInvoice(request):
    #create a blank invoice ....
    number = 'INV-'+str(uuid4()).split('-')[1]
    newInvoice = Invoice.objects.create(number=number)
    newInvoice.save()

    inv = Invoice.objects.get(number=number)
    return redirect('create-build-invoice', slug=inv.slug)




def createBuildInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Un problème est survcenu')
        return redirect('invoices')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)


    context = {}
    context['invoice'] = invoice
    context['products'] = products

    if request.method == 'GET':
        prod_form  = ProductForm()
        #prod_form = ProdSelectForm(initial_prod=products)
        
        inv_form = InvoiceForm(instance=invoice)
        client_form = ClientSelectForm(initial_client=invoice.client)
        context['prod_form'] = prod_form
        context['inv_form'] = inv_form
        context['client_form'] = client_form
        return render(request, 'invoice/create-invoice.html', context)

    if request.method == 'POST':
        prod_form  = ProductForm(request.POST)
        #prod_form  = ProdSelectForm(request.POST, )
        inv_form = InvoiceForm(request.POST, instance=invoice)
        client_form = ClientSelectForm(request.POST, initial_client=invoice.client, instance=invoice)

        if prod_form.is_valid():
            obj = prod_form.save(commit=False)
            obj.invoice = invoice
            obj.save()

            messages.success(request, "Produit ajouté avec succès")
            return redirect('create-build-invoice', slug=slug)
        elif inv_form.is_valid and 'paymentTerms' in request.POST:
            inv_form.save()

            messages.success(request, "Facture mise à jour réussi")
            return redirect('create-build-invoice', slug=slug)
        elif client_form.is_valid() and 'client' in request.POST:

            client_form.save()
            messages.success(request, "Client ajouté à la facture avec succès !")
            return redirect('create-build-invoice', slug=slug)
        else:
            context['prod_form'] = prod_form
            context['inv_form'] = inv_form
            context['client_form'] = client_form
            messages.error(request,"Un problème est survenu")
            return render(request, 'invoice/create-invoice.html', context)


    return render(request, 'invoice/create-invoice.html', context)




def viewPDFInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Un problème est survenu')
        return redirect('invoices')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    #Get Client Settings
    p_settings = Settings.objects.get(clientName='Skolo Online Learning')

    #Calculate the Invoice Total
    invoiceCurrency = ''
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y
            invoiceCurrency = x.currency



    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    context['invoiceCurrency'] = invoiceCurrency

    return render(request, 'invoice/invoice-template.html', context)


def invoice_pdf(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Un problème est survenu')
        return redirect('invoices')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    #Get Client Settings
    company = Company_Profile.objects.get(company_name = request.user.company_profile.company_name)
    #p_settings = Settings.objects.get(clientName='Skolo Online Learning')

    #Calculate the Invoice Total
    invoiceCurrency = ''
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y
            invoiceCurrency = x.currency

    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['company'] = company
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    context['invoiceCurrency'] = invoiceCurrency

    response = renderers.render_to_pdf("invoice/pdf-template.html", context)
    if response.status_code == 404:
        raise Http404("Invoice not found")

    filename = f"Invoice.pdf"

    content = f"inline; filename={filename}"
    download = request.GET.get("download")

    if download:
        content = f"attachment; filename={filename}"
    response["Content-Disposition"] = content

    return response



# def email_pdf(request, slug):
    
#     #fetch that invoice
#     try:
#         invoice = Invoice.objects.get(slug=slug)
#         pass
#     except:
#         messages.error(request, 'Un problème est survenu')
#         return redirect('invoices')

#     #fetch all the products - related to this invoice
#     products = Product.objects.filter(invoice=invoice)

#     #Get Client Settings
#     p_settings = Settings.objects.get(clientName='Skolo Online Learning')

#     #Calculate the Invoice Total
#     invoiceCurrency = ''
#     invoiceTotal = 0.0
#     if len(products) > 0:
#         for x in products:
#             y = float(x.quantity) * float(x.price)
#             invoiceTotal += y
#             invoiceCurrency = x.currency

#     context = {}
#     context['invoice'] = invoice
#     context['products'] = products
#     context['p_settings'] = p_settings
#     context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
#     context['invoiceCurrency'] = invoiceCurrency

#     template = get_template('invoice/pdf-template.html')
#     html = template.render(context)
#     result = BytesIO()

#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     pdf = result.getvalue()
#     filename = "Invoice_" + slug + '.pdf'

#     mail_subject = 'Votre Facture'
#     message = template.render(context)
#     to_email = Client.emailAddress

#     email = EmailMessage(
#         mail_subject,
#         "hello",
#         settings.EMAIL_HOST_USER,
#         [to_email]

#     )
#     email.attach(filename, pdf, 'application/pdf')
#     email.send(fail_silently=False)

#     return render(request, 'invoice/main_dashboard.html')
    


#Generate pdf using report Lab
# def invoice_pdf(request, slug):
#     #create Bytestream buffer
#     buf = io.BytesIO( )
#     #create a canvas
#     c = canvas.Canvas(buf, pagesize=letter, bottomup=0 )
#     #create a text object
#     textob = c.beginText()
#     textob.setTextOrigin(inch, inch)
#     textob.setFont("Helvetica", 14)
#     template = 'invoice/invoice-template.html'
    

#     #add some lines of text
#     # lines = [
#     #     "This is line 1"
#     #     "This is line 2"
#     #     "This is line 3"
#     # ]
#     # Loop
#     # for line in lines:
#     #     textob.textLine(line)

#     try:
#        invoice = Invoice.objects.get(slug=slug)
#        pass
#     except:
#        messages.error(request, 'Un problème est survenu')
#        return redirect('invoices')

#     #fetch all the products - related to this invoice
#     products = Product.objects.filter(invoice=invoice)

#     #Get Client Settings
#     p_settings = Settings.objects.get(clientName='Skolo Online Learning')

#     #Calculate the Invoice Total
#     invoiceCurrency = ''
#     invoiceTotal = 0.0
#     if len(products) > 0:
#         for x in products:
#             y = float(x.quantity) * float(x.price)
#             invoiceTotal += y
#             invoiceCurrency = x.currency



#     context = {}
#     context['invoice'] = invoice
#     context['products'] = products
#     context['p_settings'] = p_settings
#     context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
#     context['invoiceCurrency'] = invoiceCurrency

    
#     #Finish up 
#     c.drawText(textob)
#     c.showPage()
#     c.save()
#     buf.seek(0)

#     response = FileResponse(buf, as_attachment=True, filename='invoice.pdf')

#     #Return something
#     #return render(request, 'invoice/invoice-template.html', context)
#     #return FileResponse(buf, as_attachment=True, filename='invoice.pdf')
#     return FileResponse('invoice/invoice-template.html', context)





# def pdf(request):
#     pdf = html2pdf('invoice-template.html')
#     return HttpResponse(pdf, content_type="application/pdf")








# def viewDocumentInvoice(request, slug):
#     #fetch that invoice
#     try:
#         invoice = Invoice.objects.get(slug=slug)
#         pass
#     except:
#         messages.error(request, 'Something went wrong')
#         return redirect('invoices')

#     #fetch all the products - related to this invoice
#     products = Product.objects.filter(invoice=invoice)

#     #Get Client Settings
#     p_settings = Settings.objects.get(clientName='Skolo Online Learning')

#     #Calculate the Invoice Total
#     invoiceTotal = 0.0
#     if len(products) > 0:
#         for x in products:
#             y = float(x.quantity) * float(x.price)
#             invoiceTotal += y



#     context = {}
#     context['invoice'] = invoice
#     context['products'] = products
#     context['p_settings'] = p_settings
#     context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

#     #The name of your PDF file
#     filename = '{}.pdf'.format(invoice.uniqueId)

#     #HTML FIle to be converted to PDF - inside your Django directory
#     template = get_template('invoice/pdf-template.html')


#     #Render the HTML
#     html = template.render(context)

#     #Options - Very Important [Don't forget this]
#     options = {
#           'encoding': 'UTF-8',
#           'javascript-delay':'10', #Optional
#           'enable-local-file-access': None, #To be able to access CSS
#           'page-size': 'A4',
#           'custom-header' : [
#               ('Accept-Encoding', 'gzip')
#           ],
#       }
#       #Javascript delay is optional

#     #Remember that location to wkhtmltopdf
#     config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

#     #IF you have CSS to add to template
#     css1 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'bootstrap.min.css')
#     css2 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'main_dashboard.css')

#     #Create the file
#     file_content = pdfkit.from_string(html, False, configuration=config, options=options)

#     #Create the HTTP Response
#     response = HttpResponse(file_content, content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename = {}'.format(filename)

#     #Return
#     return response


# def emailDocumentInvoice(request, slug):
#     #fetch that invoice
#     try:
#         invoice = Invoice.objects.get(slug=slug)
#         pass
#     except:
#         messages.error(request, 'Un problème est survenu')
#         return redirect('invoices')

#     #fetch all the products - related to this invoice
#     products = Product.objects.filter(invoice=invoice)

#     #Get Client Settings
#     p_settings = Settings.objects.get(clientName='Skolo Online Learning')

#     #Calculate the Invoice Total
#     invoiceTotal = 0.0
#     if len(products) > 0:
#         for x in products:
#             y = float(x.quantity) * float(x.price)
#             invoiceTotal += y



#     context = {}
#     context['invoice'] = invoice
#     context['products'] = products
#     context['p_settings'] = p_settings
#     context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

#     #The name of your PDF file
#     filename = '{}.pdf'.format(invoice.uniqueId)

#     #HTML FIle to be converted to PDF - inside your Django directory
#     template = get_template('invoice/pdf-template.html')


#     #Render the HTML
#     html = template.render(context)

#     #Options - Very Important [Don't forget this]
#     options = {
#           'encoding': 'UTF-8',
#           'javascript-delay':'1000', #Optional
#           'enable-local-file-access': None, #To be able to access CSS
#           'page-size': 'A4',
#           'custom-header' : [
#               ('Accept-Encoding', 'gzip')
#           ],
#       }
#       #Javascript delay is optional

#     #Remember that location to wkhtmltopdf
#     config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

#     #Saving the File
#     filepath = os.path.join(settings.MEDIA_ROOT, 'client_invoices')
#     os.makedirs(filepath, exist_ok=True)
#     pdf_save_path = filepath+filename
#     #Save the PDF
#     pdfkit.from_string(html, pdf_save_path, configuration=config, options=options)


#     #send the emails to client
#     to_email = invoice.client.emailAddress
#     from_client = p_settings.clientName
#     emailInvoiceClient(to_email, from_client, pdf_save_path)

#     invoice.status = 'EMAIL_SENT'
#     invoice.save()

#     #Email was send, redirect back to view - invoice
#     messages.success(request, "Email sent to the client succesfully")
#     return redirect('create-build-invoice', slug=slug)








def deleteInvoice(request, slug):
    try:
        Invoice.objects.get(slug=slug).delete()
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    return redirect('invoices')




# def companySettings(request):
    
#     company = SettingsForm()
    
#     if request.method == 'POST':
#         company = SettingsForm(request.POST)
#         if company.is_valid():
#             company.save()
#     context = {'company': company}
#     return render(request, 'invoice/company-settings.html', context)
































###
##
#