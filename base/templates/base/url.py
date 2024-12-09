from django.urls import path
from . import views



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),  
    path("find/", views.find_university_view, name="find_university"),  # Add this line
]
