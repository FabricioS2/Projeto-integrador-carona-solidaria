from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario,Carona, Veiculo
import re
from django.utils import timezone

class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=100, required=True)
    documento = forms.CharField(max_length=14, required=True)
    email = forms.EmailField(required=True)
    telefone = forms.CharField(max_length=15, required=True)
    perfil = forms.ChoiceField(choices=[('motorista', 'Motorista'), ('passageiro', 'Passageiro')], required=True)
    tipo_campus = forms.ChoiceField(choices=[('Campus Natal-Central', 'Campus Natal-Central'), ('Campus Mossoró', 'Campus Mossoró'), ('Campus Parnamirim', 'Campus Parnamirim'), ('Campus Pau dos Ferros', 'Campus Pau dos Ferros')], required=True)
    foto = forms.ImageField(required=True)
    senha = forms.CharField(widget=forms.PasswordInput, required=True)
    
    # Campos opcionais para motorista
    modelo = forms.CharField(max_length=50, required=False)
    placa = forms.CharField(max_length=10, required=False)
    cor = forms.CharField(max_length=20, required=False)
    assentos = forms.IntegerField(required=False, min_value=1)
    tipo_veiculo = forms.ChoiceField(choices=[('Moto', 'MoMoto'), ('Carro', 'Carro')], required=False)

    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        
        # Remove caracteres não numéricos
        documento_limpo = re.sub(r'\D', '', documento)
        
        # Verifica se CPF já existe
        if Usuario.objects.filter(cpf=documento_limpo).exists():
            raise ValidationError('Este CPF já está cadastrado.')
        
        return documento_limpo
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Normaliza o e-mail (remove espaços)
        email_limpo = email.strip()

        # Verifica se o email já existe
        if Usuario.objects.filter(email=email_limpo).exists():
            raise ValidationError('Este e-mail já está cadastrado.')

        return email_limpo
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        # Remove tudo que não for número
        telefone_limpo = re.sub(r'\D', '', telefone)

        # Verifica se telefone já existe
        if Usuario.objects.filter(telefone=telefone_limpo).exists():
            raise ValidationError('Este telefone já está cadastrado.')

        return telefone_limpo


    
    def clean(self):
        cleaned_data = super().clean()
        perfil = cleaned_data.get('perfil')
        
        # Valida campos obrigatórios para motorista
        if perfil == 'motorista':
            if not cleaned_data.get('modelo'):
                self.add_error('modelo', 'Este campo é obrigatório para motoristas.')
            if not cleaned_data.get('placa'):
                self.add_error('placa', 'Este campo é obrigatório para motoristas.')
            if not cleaned_data.get('cor'):
                self.add_error('cor', 'Este campo é obrigatório para motoristas.')
            if not cleaned_data.get('assentos'):
                self.add_error('assentos', 'Este campo é obrigatório para motoristas.')

        
        return cleaned_data
    

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        error_messages={
            "required": "Informe o email.",
            "invalid": "Informe um email válido.",
        }
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        error_messages={
            "required": "Informe a senha.",
        }
    )

    remember_me = forms.BooleanField(required=False)




class CaronaForm(forms.ModelForm):
    class Meta:
        model = Carona
        fields = ['veiculo', 'horario_e_data', 'origem', 'destino', 'vagas_disponiveis']
        widgets = {
            'horario_e_data': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'origem': forms.TextInput(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'Digite o local de saída'
                }
            ),
            'destino': forms.TextInput(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'Digite o local de destino'
                }
            ),
            'vagas_disponiveis': forms.NumberInput(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'min': 1,
                    'max': 10
                }
            ),
            'veiculo': forms.Select(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
        }
    
    def __init__(self, usuario, *args, **kwargs):
        super(CaronaForm, self).__init__(*args, **kwargs)
        # Filtra veículos apenas do usuário motorista
        self.fields['veiculo'].queryset = Veiculo.objects.filter(motorista=usuario)
        # Define o valor mínimo para horário (agora)
        self.fields['horario_e_data'].initial = timezone.now() + timezone.timedelta(hours=1)
    
    def clean_horario_e_data(self):
        horario = self.cleaned_data['horario_e_data']
        if horario < timezone.now():
            raise forms.ValidationError("O horário não pode ser no passado!")
        return horario