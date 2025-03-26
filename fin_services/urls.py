from django.urls import path 
from .views import HomePageView, submit_query, ServicesPageView, SubmitServiceFormView, search_services, submit_consultation
from .views import PrivacyPageView, TermsPageView, AboutPageView, ContactPageView, ConsultPageView, FaqPageView, ProductsPageView, PaymentCallbackView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('search-services/', search_services, name='search_services'),
    path('services/<slug:slug>/', ServicesPageView.as_view(), name='services_page'),
    path('submit-query/', submit_query, name='submit_query'),
    path('submit-service-form/', SubmitServiceFormView.as_view(), name='submit_service_form'),
    path('submit-consultation/', submit_consultation, name='submit_consultation'),
    path("about/", AboutPageView.as_view(), name="about"),
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("consult/", ConsultPageView.as_view(), name="consult"),
    path("faq/", FaqPageView.as_view(), name="faq"),
    path("products/<int:product_id>/", ProductsPageView.as_view(), name="products"),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path("privacy/", PrivacyPageView.as_view(), name="privacy"),
    path("terms/", TermsPageView.as_view(), name="terms"),
]