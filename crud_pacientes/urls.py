from django.urls import path
from .views import (
    DateFormAddView, 
    CodigosPromocionalesView, 
    HorariosDisponiblesView, 
    ReservarHorarioView, 
    ListarServiciosView, 
    ListarEspecialistasView, 
    process_payment,
    ComentariosPacientesView,
    add_comment,
    delete_comment,
    UserProfileView,
    get_authenticated_user,
    obtener_citas,
    ModificarCitaView,
    CancelarCitaView
)

urlpatterns = [
    path('api/add-date/', DateFormAddView.as_view(), name='add_date'),
    path('api/codigo-promocional/', CodigosPromocionalesView.as_view(), name='codigo_promocional'),
    path('api/horarios-disponibles/', HorariosDisponiblesView.as_view(), name='horarios_disponibles'),
    path('api/reservar-horario/', DateFormAddView.as_view(), name='reservar_horario'),
    path('api/servicios/', ListarServiciosView.as_view(), name='listar_servicios'),
    path('api/especialistas/', ListarEspecialistasView.as_view(), name='especialistas'),
    path('api/process-payment/', process_payment, name='process_payment'),
    path('api/comentarios-pacientes/', ComentariosPacientesView.as_view(), name='listar_comentarios_pacientes'),
    path('api/comentarios/add/', add_comment, name='add_comment'),
    path('api/comentarios/delete/', delete_comment, name='delete_comment'),
    path('api/user/', UserProfileView.as_view(), name='user_profile'),  # Ajuste para coherencia con otras rutas API
    path('api/auth/user/', get_authenticated_user, name='get_authenticated_user'),
    path("api/obtener-citas/", obtener_citas, name="obtener-citas"),
    path('api/citas/<uuid:id_citas>/modificar/', ModificarCitaView.as_view(), name='modificar-cita'),
    path('api/citas/<uuid:id_citas>/cancelar/', CancelarCitaView.as_view(), name='cancelar-cita'),
]
