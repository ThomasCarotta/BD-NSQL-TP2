from django.urls import path
from . import views

urlpatterns = [
    path('capitulos/', views.listar_capitulos, name='listar_capitulos'),
    path('capitulos/<int:temporada>/<int:capitulo>/reservar/', views.reservar_capitulo, name='reservar_capitulo'),
    path('capitulos/<int:temporada>/<int:capitulo>/pagar/', views.confirmar_pago, name='confirmar_pago'),
]
