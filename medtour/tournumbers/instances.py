import os


def get_shots_path(instance, filename):
    return os.path.join('shots',
                        "tour_%s" % str(instance.tour_number.tour.id),
                        "number_%s" % str(instance.tour_number.id),
                        filename)
