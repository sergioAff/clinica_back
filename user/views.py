from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .serializers import UserSerializer
from crud_pacientes.models import CustomUser
import json 
from django.shortcuts import render
from crud_pacientes.models import Cita
from django.utils.decorators import method_decorator


@csrf_exempt
@require_http_methods(["PUT"])
def update_user(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        user = get_object_or_404(CustomUser, email=email)

        # Actualiza los campos del usuario
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.sexo = data.get("sexo", user.sexo)
        user.fecha_nacimiento = data.get("fecha_nacimiento", user.fecha_nacimiento)
        user.direccion = data.get("direccion", user.direccion)
        user.telefono = data.get("telefono", user.telefono)
        user.fecha_ingreso = data.get("fecha_ingreso", user.fecha_ingreso)
        user.notas_adicionales = data.get("notas_adicionales", user.notas_adicionales)
        # user.edad = data.get("edad", user.edad)

        user.save()

        return JsonResponse({"message": "Usuario actualizado exitosamente."}, status=200)
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request):
    token = request.COOKIES.get('jet') or request.headers.get('Authorization')

    if not token:
        return JsonResponse({"message": "No hay sesión activa."}, status=400)

    if token.startswith('Token '):
        token = token.split(' ')[1]

    try:
        token_instance = Token.objects.get(key=token)
        user = token_instance.user

        # Elimina las relaciones de grupos y permisos
        user.groups.clear()  # Elimina las relaciones con grupos
        user.user_permissions.clear()  # Elimina las relaciones con permisos

        # Elimina el usuario
        user.delete()

        # Borra el token del usuario
        token_instance.delete()

        response = JsonResponse({"message": "Cuenta eliminada exitosamente."}, status=200)
        response.delete_cookie('jet')
        return response
    except Token.DoesNotExist:
        return JsonResponse({"message": "Token inválido o expirado."}, status=400)
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)



class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)        
            except IntegrityError:
                return Response({'message': 'Ya existe una cuenta con este correo electrónico.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({'message': 'Error al crear cuenta.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jet')
        if token and Token.objects.filter(key=token).exists():
            return Response({"message": "Ya hay una sesión activa."}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            response = Response({
                "message": "Inicio de sesión exitoso.",
                "token": token.key
            }, status=status.HTTP_200_OK)
            response.set_cookie(key='jet', value=token.key, httponly=True)
            return response
        return Response({"message": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogOutView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jet')
        if not token:
            return Response({"message": "No hay ninguna sesión activa."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_instance = Token.objects.get(key=token)
            token_instance.delete()
        except Token.DoesNotExist:
            return Response({"message": "No hay ninguna sesión activa."}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)
        response.delete_cookie('jet')
        return response