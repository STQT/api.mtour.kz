from io import BytesIO

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from weasyprint import HTML, CSS

from .models import ServiceCart, Payment


def generate_pdf(payment_obj: Payment):
    # Get the report object
    service_cart: ServiceCart = payment_obj.cart
    # Generate the PDF file
    html_template = get_template('check/report.html')
    html_string = html_template.render({'report': service_cart})
    html = HTML(string=html_string)
    css_path = staticfiles_storage.path('css/check.css')
    check_css_path = staticfiles_storage.path('css/stylesheet.css')
    css = CSS(filename=css_path)
    check_css = CSS(filename=check_css_path)
    result = BytesIO()
    html.write_pdf(result, stylesheets=[css, check_css])
    # Save the PDF file to the model
    payment_obj.pdf_file.save('report.pdf', result, save=True)
