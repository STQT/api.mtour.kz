import os


def get_price_path(instance, filename):
    return os.path.join('prices', "price_%s" % str(instance.id), filename)


def get_shots_path(instance, filename):
    return os.path.join('shots', "tour_%s" % str(instance.tour.id), filename)
