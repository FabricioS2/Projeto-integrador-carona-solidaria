from django.db import models
from .validators import validar_cpf,validar_ano,validar_capacidade
# Create your models here.

class Usuario(models.Model):
    TIPO_CHOICES = [('Motorista', 'Motorista'), ('Passageiro', 'Passageiro')]
    TIPO_CAMPUS = [('Campus Natal-Central', 'Campus Natal-Central'), ('Campus Mossoró', 'Campus Mossoró'), ('Campus Parnamirim', 'Campus Parnamirim'), ('Campus Pau dos Ferros', 'Campus Pau dos Ferros')]
    tipo_usuario = models.CharField(max_length=50, choices=TIPO_CHOICES)
    tipo_campus = models.CharField(max_length=50, choices=TIPO_CAMPUS)
    nome =models.CharField(max_length=255,blank=False, null=False)
    telefone = models.CharField(max_length=15,blank=False, null=False)
    email = models.EmailField(unique=True,blank=False, null=False)
    cpf = models.CharField(max_length=14,unique=True,validators=[validar_cpf])
    senha = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    is_motorista = models.BooleanField(default=False,blank=False, null=False)

    def __str__(self):
        return f"{self.nome}"

class Veiculo(models.Model):
    TIPO_VEICULO = [('Moto', 'Moto'), ('Carro', 'Carro')]
    tipo_veiculo = models.CharField(max_length=50, choices=TIPO_VEICULO)
    modelo = models.CharField(max_length=125)
    marca = models.CharField(max_length=50)
    ano = models.IntegerField(validators=[validar_ano])
    cor = models.CharField(max_length=50)
    placa = models.CharField(max_length=7, unique=True)
    capacidade = models.IntegerField(validators=[validar_capacidade])
    motorista = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.modelo} - {self.placa} - {self.motorista}"      


class Carona(models.Model):
    STATUS_CHOICES = [
        ('Agendada', 'Agendada'), 
        ('Em Andamento', 'Em Andamento'), 
        ('Finalizada', 'Finalizada'), 
        ('Cancelada', 'Cancelada')
    ]
    
    motorista = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,  
        related_name='caronas_como_motorista'
    )
    veiculo = models.ForeignKey( 
        Veiculo, 
        on_delete=models.CASCADE,
        related_name='caronas_veiculo'
    )
    horario_e_data = models.DateTimeField()
    origem = models.CharField(max_length=125)
    destino = models.CharField(max_length=125)
    vagas_disponiveis = models.IntegerField(
        validators=[validar_capacidade],
        default=1
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Agendada'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.motorista} - {self.horario_e_data} - {self.status}"


class SolicitacaoCarona(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'), 
        ('Aceita', 'Aceita'), 
        ('Recusada', 'Recusada')
    ]
    
    carona = models.ForeignKey(
        Carona, 
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )
    passageiro = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='solicitacoes_caronas',
        default=1,  # ID de um usuário existente ou null=True temporariamente
        null=True   # Permitir nulo temporariamente
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pendente'
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['carona', 'passageiro']

    def __str__(self):
        return f"{self.passageiro.nome if self.passageiro else 'Sem passageiro'} - {self.carona} - {self.status}"
    
    
class MensagemChat(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.data_envio}"  