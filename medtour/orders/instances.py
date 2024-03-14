import os


def get_pdf_path(instance, filename):
    return os.path.join('pdf_files', "user_%s" % str(instance.user.id), filename)
