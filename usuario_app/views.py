from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from .models import Usuario, Veiculo
from django.contrib import messages
from .forms import CadastroForm

def chat(request):
    return render(request, 'usuario_app/chat.html')

def perfil(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")

    usuario = Usuario.objects.get(id=usuario_id)
    veiculos = Veiculo.objects.filter(motorista=usuario)

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        email = request.POST.get("email", "").strip()
        motorista = request.POST.get("motorista", "Não")

        # atualiza usuario
        usuario.nome = nome or usuario.nome
        usuario.telefone = telefone or usuario.telefone
        usuario.email = email or usuario.email

        if motorista == "Sim":
            usuario.tipo_usuario = "Motorista"
            usuario.is_motorista = True
        else:
            usuario.tipo_usuario = "Passageiro"
            usuario.is_motorista = False
        
        # Processar upload da foto
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            if foto.size > 5 * 1024 * 1024:
                messages.error(request, "A foto deve ter menos de 5MB.")
            elif not foto.content_type.startswith('image/'):
                messages.error(request, "Por favor, envie apenas imagens.")
            else:
                usuario.foto = foto

        usuario.save()

        # REMOÇÕES
        veiculos_removidos = request.POST.get("veiculos_removidos", "")
        if veiculos_removidos:
            ids = [i for i in veiculos_removidos.split(',') if i.strip().isdigit()]
            if ids:
                Veiculo.objects.filter(id__in=ids, motorista=usuario).delete()

        # PROCESSAR VEÍCULOS - COM VALIDAÇÃO MELHORADA
        if usuario.is_motorista:
            tipos = request.POST.getlist("veiculo_tipo")
            modelos = request.POST.getlist("veiculo_modelo")
            placas = request.POST.getlist("veiculo_placa")
            cores = request.POST.getlist("veiculo_cor")
            capacidades = request.POST.getlist("veiculo_lugares")
            anos = request.POST.getlist("veiculo_ano")
            ids = request.POST.getlist("veiculo_id")

            veiculos_validos = 0
            veiculos_com_erro = 0

            for i in range(len(tipos)):
                tipo = tipos[i].strip() if i < len(tipos) else ""
                modelo = modelos[i].strip() if i < len(modelos) else ""
                placa = placas[i].strip() if i < len(placas) else ""
                cor = cores[i].strip() if i < len(cores) else ""
                capacidade = capacidades[i].strip() if i < len(capacidades) else ""
                ano = anos[i].strip() if i < len(anos) else ""
                vid = ids[i].strip() if i < len(ids) else ""

                # VALIDAÇÃO FORTE - defina quais campos são obrigatórios
                campos_obrigatorios = [
                    (modelo, "modelo"),
                    (placa, "placa"), 
                    (tipo, "tipo de veículo"),
                    (ano, "ano")
                ]

                campos_faltantes = [nome for valor, nome in campos_obrigatorios if not valor]
                
                if campos_faltantes:
                    veiculos_com_erro += 1
                    messages.error(
                        request, 
                        f"Veículo {i+1}: Campos obrigatórios faltando: {', '.join(campos_faltantes)}"
                    )
                    continue

                # Validação numérica
                try:
                    capacidade_int = int(capacidade) if capacidade else 1
                    if capacidade_int < 1 or capacidade_int > 10:
                        messages.error(request, f"Veículo {modelo}: Capacidade deve ser entre 1 e 10")
                        veiculos_com_erro += 1
                        continue
                except ValueError:
                    messages.error(request, f"Veículo {modelo}: Capacidade inválida")
                    veiculos_com_erro += 1
                    continue

                try:
                    ano_int = int(ano)
                    if ano_int < 1900 or ano_int > 2030:
                        messages.error(request, f"Veículo {modelo}: Ano deve ser entre 1900 e 2030")
                        veiculos_com_erro += 1
                        continue
                except ValueError:
                    messages.error(request, f"Veículo {modelo}: Ano inválido")
                    veiculos_com_erro += 1
                    continue

                # Se passou por todas as validações, salva o veículo
                try:
                    if vid:
                        v = Veiculo.objects.get(id=vid, motorista=usuario)
                        v.tipo_veiculo = tipo
                        v.modelo = modelo
                        v.placa = placa
                        v.cor = cor
                        v.capacidade = capacidade_int
                        v.ano = ano_int
                        v.save()
                    else:
                        Veiculo.objects.create(
                            motorista=usuario,
                            tipo_veiculo=tipo,
                            modelo=modelo,
                            placa=placa,
                            cor=cor,
                            capacidade=capacidade_int,
                            ano=ano_int
                        )
                    veiculos_validos += 1
                    
                except Exception as e:
                    messages.error(request, f"Erro ao salvar veículo {modelo}: {str(e)}")
                    veiculos_com_erro += 1

            # Feedback resumido
            if veiculos_validos > 0:
                messages.success(request, f"{veiculos_validos} veículo(s) salvo(s) com sucesso!")
            if veiculos_com_erro > 0:
                messages.warning(request, f"{veiculos_com_erro} veículo(s) não foram salvos devido a erros.")

        else:
            Veiculo.objects.filter(motorista=usuario).delete()

        return redirect("perfil")
    
    return render(request, "usuario_app/perfil.html", {
        "usuario": usuario,
        "veiculos": veiculos,
    })


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
