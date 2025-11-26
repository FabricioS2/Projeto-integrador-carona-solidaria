from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from .models import Usuario, Veiculo
from django.contrib import messages
from .forms import CadastroForm


def chat(request):
    return render(request, 'usuario_app/chat.html')

def perfil(request):
    return render(request, 'usuario_app/perfil.html')

def historico(request):
    return render(request, 'usuario_app/historico.html')

def cadastrar_carona(request):
    return render(request, 'usuario_app/cadastrar_carona.html')

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Recupera os dados validados
            dados = form.cleaned_data
            
            try:
                # Cria usuário
                usuario = Usuario.objects.create(
                    nome=dados['nome'],
                    cpf=dados['documento'],
                    email=dados['email'],
                    telefone=dados['telefone'],
                    tipo_campus=dados['tipo_campus'],
                    foto=dados['foto'],
                    tipo_usuario=dados['perfil'].capitalize(),
                    is_motorista=(dados['perfil'] == "motorista"),
                    senha=make_password(dados['senha'])
                )

                # Se for motorista → salvar veículo
                if dados['perfil'] == "motorista":
                    Veiculo.objects.create(
                        motorista=usuario,
                        modelo=dados['modelo'],
                        placa=dados['placa'],
                        cor=dados['cor'],
                        capacidade=dados['assentos'],
                    )

                messages.success(request, 'Cadastro realizado com sucesso!')
                return redirect("login")
                
            except Exception as e:
                messages.error(request, f'Erro ao criar usuário: {str(e)}')
        else:
            # Se o formulário não for válido, mostra os erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    else:
        form = CadastroForm()
    
    return render(request, 'usuario_app/cadastro.html', {'form': form})


def login(request):
    # Se já estiver logado, redireciona
    if request.session.get("usuario_id"):
        return redirect("solicitar_carona")
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("password", "")
        remember_me = request.POST.get("remember-me")

        if not email or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "usuario_app/login.html", {
                "email_value": email
            })

        try:
            usuario = Usuario.objects.get(email=email)

            if check_password(senha, usuario.senha):
                # Login bem-sucedido
                request.session["usuario_id"] = usuario.id
                
                # Configura tempo da sessão baseado em "Lembrar-me"
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(0)  # Fecha ao sair do browser
                
                return redirect("solicitar_carona")   
            else:
                messages.error(request, "Senha incorreta. Tente novamente.")
                return render(request, "usuario_app/login.html", {
                    "email_value": email
                })

        except Usuario.DoesNotExist:
            messages.error(request, 
                "Email não encontrado. Verifique o email ou cadastre-se.")
            return render(request, "usuario_app/login.html", {
                "email_value": email
            })

    return render(request, "usuario_app/login.html")

def solicitar_carona(request):
    return render(request, 'usuario_app/solicitar_carona.html')
