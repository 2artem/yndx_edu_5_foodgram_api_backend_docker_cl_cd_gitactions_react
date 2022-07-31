from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('admin/', admin.site.urls),
]
