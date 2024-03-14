from django.contrib.sitemaps import Sitemap

from .models import Tour


class TourSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Tour.objects.filter(is_moderated=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return '/%s/%s' % (obj.category.slug, obj.slug)
