from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView, \
    SpectacularJSONAPIView

from medtour.tours.sitemaps import TourSitemap
from medtour.users.views import CookieTokenRefreshView, CookieTokenObtainPairView, \
    CookieTokenLogoutView, VerifyCodeView, ResetPassword  # Import the above views

sitemaps = {
    "tours": TourSitemap,
}


urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("medtour.users.mvt_urls", namespace="users")),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("accounts/", include("phone_auth.urls")),
    # path("oauth2/callback/apple/", apple_callback),

]
# urlpatterns += [path('i18n/', include('django.conf.urls.i18n')),]

# urlpatterns += i18n_patterns(path(settings.ADMIN_URL, admin.site.urls),)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("v1/", include("config.api_router"), name="v1"),
    path("docs/", include("medtour.pages.urls")),
    path('api/auth/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/logout/', CookieTokenLogoutView.as_view(), name='token_refresh_logout'),
    path('api/auth/verify/', VerifyCodeView.as_view(), name='verify_code'),
    path('api/auth/resetPassword/', ResetPassword.as_view(), name='reset_password'),
    # DRF auth token
    # path("auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc'),
    path('api/schema/json/', SpectacularJSONAPIView.as_view(), name='json'),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

admin.site.site_title = "СуперАдминка MedTour"
admin.site.site_header = "СуперАдминка MedTour"
admin.site.site_url = "https://mtour.kz"
admin.site.index_title = "MTour.kz"
