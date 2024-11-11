from rest_framework import serializers
from .models import CustomUser, CodigosPromocionales, HorarioDisponible, Servicio, Especialista, Cita

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'sexo', 'fecha_nacimiento', 'direccion', 'telefono', 
            'fecha_ingreso', 'notas_adicionales', 
            'edad', 'comentarios'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class DescuentosPromocionalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigosPromocionales
        fields = '__all__'

class HorarioDisponibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioDisponible
        fields = ['id', 'fecha', 'hora', 'disponible']

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class EspecialistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialista
        fields = '__all__'

class CitaSerializer(serializers.ModelSerializer):
    # paciente_id = UserSerializer(read_only=True)

    class Meta:
        model = Cita
        fields = [
            'id_citas', 'paciente_id', 'fecha', 
            'hora', 'servicio',"monto"
        ]
