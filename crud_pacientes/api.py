from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

class PacientesViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def toggle_done(self, request, pk=None):
        paciente = self.get_object()
        paciente.done = not paciente.done
        paciente.save()
        message = 'Tarea realizada' if paciente.done else 'Estado revertido'
        return Response({'status': message}, status=status.HTTP_200_OK)
