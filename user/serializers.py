from rest_framework import serializers
from crud_pacientes.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'first_name', 'last_name', 
            'sexo', 'fecha_nacimiento', 'direccion', 
            'telefono', 'fecha_ingreso', 'notas_adicionales', 
            'comentarios', 'edad'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'fecha_ingreso': {'read_only': True},
            'edad': {'read_only': True},
            'email': {'required': True},
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
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance