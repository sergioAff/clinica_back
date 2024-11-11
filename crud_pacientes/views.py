from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import stripe
import json
import uuid
from .models import CustomUser, CodigosPromocionales, HorarioDisponible, Servicio, Especialista, Cita
from .serializers import (UserSerializer, DescuentosPromocionalesSerializer, 
                          HorarioDisponibleSerializer, ServicioSerializer, 
                          EspecialistaSerializer, CitaSerializer)

# Configuración de la clave secreta de Stripe
stripe.api_key = 'sk_test_51PsVUa094T9Rbqk51EM7Kk0F1Fne4ajX225mI2n2cglTqlK85Yfnzyf4hcjiuvqO6SMuLeChk2tG9ii65NI1ghIZ00qrjRZamC'

@api_view(['GET'])
def get_authenticated_user(request):
    if not request.user.is_authenticated:
        return Response({'message': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user
    return Response({'email': user.email}, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ComentariosPacientesView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
def add_comment(request):
    if not request.user.is_authenticated:
        return Response({'message': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    email = request.data.get('email')
    comentario = request.data.get('comentario')

    user = get_object_or_404(CustomUser, email=email)
    user.comentarios = comentario
    user.save()
    return Response({'message': 'Comentario guardado exitosamente'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_comment(request):
    if not request.user.is_authenticated:
        return Response({'message': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    email = request.data.get('email')
    user = get_object_or_404(CustomUser, email=email)

    if request.user.email != email:
        return Response({'message': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

    user.comentarios = ""
    user.save()
    return Response({'message': 'Comentario eliminado exitosamente'}, status=status.HTTP_200_OK)

class DateFormAddView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        
        # Buscar el usuario por email
        paciente_id = CustomUser.objects.filter(email=email).first()
        
        if paciente_id:
            serializer = self.get_serializer(paciente_id, data=request.data, partial=True)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        paciente_id = serializer.save()

        # # Validar el número de citas existentes para el paciente
        # citas_existentes = Cita.objects.filter(paciente_id=email).count()
        # if citas_existentes >= 3:
        #     return Response({"error": "No se puede agendar más de 3 citas."}, status=status.HTTP_400_BAD_REQUEST)

        # Datos de la cita que provienen del frontend
        cita_data = {
            "id_citas": uuid.uuid4(),
            "paciente_id": email,
            "fecha": request.data.get('fecha'),
            "hora": request.data.get('hora'),
            "servicio": request.data.get('servicio'),
            "monto": request.data.get('monto', 0),
        }

        # Serializar y guardar la cita
        cita_serializer = CitaSerializer(data=cita_data)

        if cita_serializer.is_valid():
            cita_serializer.save()
        else:
            return Response(cita_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Aquí llamamos a la función que reserva el horario
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')

        # Obtener el horario disponible
        horario = get_object_or_404(HorarioDisponible, fecha=fecha, hora=hora)

        # Verificar si el horario está disponible
        if not horario.disponible:
            return Response({"error": "El horario ya está reservado."}, status=status.HTTP_400_BAD_REQUEST)

        # Reservar el horario
        horario.disponible = False
        horario.save()

        # Respuesta final
        return Response({
            'message': 'Cita creada y horario reservado exitosamente.',
            'cita': cita_serializer.data
        }, status=status.HTTP_201_CREATED)


class CodigosPromocionalesView(generics.GenericAPIView):
    def get(self, request):
        codigo = request.query_params.get('codigo')
        if not codigo:
            return Response({'error': 'Código no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

        codigo_promo = CodigosPromocionales.objects.filter(codigo=codigo).first()
        if codigo_promo:
            return Response({'descuento': codigo_promo.descuento}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Código inválido'}, status=status.HTTP_404_NOT_FOUND)

class HorariosDisponiblesView(generics.ListAPIView):
    serializer_class = HorarioDisponibleSerializer

    def get_queryset(self):
        fecha = self.request.query_params.get('fecha')
        return HorarioDisponible.objects.filter(fecha=fecha, disponible=True).order_by('hora')

class ReservarHorarioView(APIView):
    def patch(self, request):
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')

        horario = get_object_or_404(HorarioDisponible, fecha=fecha, hora=hora)

        if not horario.disponible:
            return Response({"error": "El horario ya está reservado."}, status=status.HTTP_400_BAD_REQUEST)

        horario.disponible = False
        horario.save()
        return Response({"message": "Horario reservado exitosamente."}, status=status.HTTP_200_OK)

class ListarServiciosView(generics.ListAPIView):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class ListarEspecialistasView(generics.ListAPIView):
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=1000,  # Monto en centavos
                currency='usd',
                payment_method=token,
                confirmation_method='manual',
                confirm=True,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@api_view(['GET'])
def obtener_citas(request):
    email = request.GET.get('email') 
    try:
        citas = Cita.objects.filter(paciente_id=email)  # Buscar citas por paciente_id
        citas_data = [
            {   "id_cita":cita.id_citas,
                "idservicio": cita.servicio,
                "fecha": cita.fecha.strftime("%Y-%m-%d"),
                "hora": cita.hora.strftime("%H:%M")
            }
            for cita in citas
        ]
        return JsonResponse({"citas": citas_data}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

class ModificarCitaView(generics.UpdateAPIView):
    queryset = Cita.objects.all()
    lookup_field = 'id_citas'
    serializer_class = CitaSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Permitir actualizaciones parciales
        instance = self.get_object()

        # Enviar solo los datos que realmente se quieren modificar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class CancelarCitaView(generics.DestroyAPIView):
    queryset = Cita.objects.all()
    lookup_field = 'id_citas'
    serializer_class = CitaSerializer
    

    def delete(self, request, *args, **kwargs):
        # Obtener la cita que se va a cancelar
        cita = self.get_object()

        # Obtener los detalles del horario asociado a la cita (fecha y hora)
        fecha = cita.fecha
        hora = cita.hora

        # Recuperar el objeto HorarioDisponible correspondiente
        horario = get_object_or_404(HorarioDisponible, fecha=fecha, hora=hora)

        # Marcar el horario como disponible nuevamente
        horario.disponible = True
        horario.save()

        response = super().delete(request, *args, **kwargs)

        return Response({"message": "Cita cancelada"}, status=status.HTTP_200_OK)
