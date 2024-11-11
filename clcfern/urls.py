from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('crud_pacientes.urls')),
    path("", include('user.urls'))
]
