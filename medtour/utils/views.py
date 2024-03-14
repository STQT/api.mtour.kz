import os

from django.http import HttpResponse
from django.views import View
from rest_framework.views import APIView
from weasyprint.text.fonts import FontConfiguration

from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.conf import settings


class GeneratePDF(View):
    def get(self, request):
        # Get the report object
        font_config = FontConfiguration()
        # Generate the PDF file
        html_template = get_template('check/report.html')
        html_string = html_template.render({'report': {"foo": "bar"}})
        html = HTML(string=html_string)
        # css_path = staticfiles_storage.path('css/check.css')
        css_path = os.path.join(settings.ROOT_DIR, 'medtour/static/css/check.css')
        # check_css_path = staticfiles_storage.path('css/stylesheet.css')
        check_css_path = os.path.join(settings.ROOT_DIR, 'medtour/static/css/stylesheet.css')
        css = CSS(filename=css_path, font_config=font_config)
        check_css = CSS(filename=check_css_path, font_config=font_config)
        # result = BytesIO()
        pdf_file = html.write_pdf(
            # result,
            stylesheets=[css, check_css])
        # Save the PDF file to the model
        # Payment.objects.get(id=24).pdf_file.save('report.pdf', pdf_file, save=True)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="my_pdf.pdf"'
        return response
