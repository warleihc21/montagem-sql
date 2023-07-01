from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('index/', views.index, name='index'),
    path('safra/', views.safra, name='safra'),
    path('bradesco/', views.bradesco, name='bradesco'),
    path('filtrar_dados/', views.filtrar_dados, name='filtrar_dados'),
    path('resultado_filtro/', views.resultado_filtro, name='resultado_filtro'),
    path('export_csv/', views.export_csv, name='export_csv'),



    


    

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)