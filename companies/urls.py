from django.urls import path

from . import views

urlpatterns = [
    path("load-company-data/", views.LoadCompanyData.as_view()),
    path("get-company-data/", views.GetCompanyData.as_view()),
]