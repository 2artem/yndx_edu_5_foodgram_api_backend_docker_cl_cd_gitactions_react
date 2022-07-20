from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('admin/', admin.site.urls),
]
