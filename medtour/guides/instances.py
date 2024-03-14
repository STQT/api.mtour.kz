import os


def get_program_path(instance, filename):
    return os.path.join('program_shots', "program_%s" % str(instance.program.id), filename)
