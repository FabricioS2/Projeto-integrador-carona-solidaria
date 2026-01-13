from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password,check_password
from .models import Usuario, Veiculo, MensagemChat, Carona,SolicitacaoCarona
from django.contrib import messages
from .forms import CadastroForm,LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import CaronaForm 
from django.db.models import Q
from datetime import datetime, date



def chat(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    usuario = Usuario.objects.get(id=usuario_id)
    
    # Busca as mensagens antigas (todas ou limite as últimas 50)
    mensagens_antigas = MensagemChat.objects.select_related('usuario').all()
    
    return render(request, 'usuario_app/chat.html', {
        'usuario': usuario,
        'mensagens_antigas': mensagens_antigas # Passa para o template
    })


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
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Verifica se o usuário é motorista
    if not usuario.is_motorista:
        messages.error(request, "Apenas motoristas podem criar caronas.")
        return redirect("solicitar_carona")
    
    # Verifica se o usuário tem veículos cadastrados
    veiculos = Veiculo.objects.filter(motorista=usuario)
    if not veiculos.exists():
        messages.error(request, "Você precisa cadastrar um veículo antes de criar uma carona.")
        return redirect("perfil")
    
    # Processa o formulário se for POST
    if request.method == "POST":
        form = CaronaForm(usuario, request.POST)
        if form.is_valid():
            carona = form.save(commit=False)
            carona.motorista = usuario
            carona.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Carona criada com sucesso!'
                })
            else:
                messages.success(request, "Carona criada com sucesso!")
                return redirect("cadastrar_carona")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = CaronaForm(usuario)
    
    # Busca TODAS as caronas do usuário que NÃO ESTÃO FINALIZADAS
    # Independente de serem passadas ou futuras
    caronas = Carona.objects.filter(
        motorista=usuario
    ).exclude(
        status='Finalizada'  # Exclui apenas caronas já finalizadas
    ).order_by('horario_e_data')
    
    context = {
        'usuario': usuario,
        'form': form,
        'caronas': caronas,
        'veiculos': veiculos,
    }
    return render(request, 'usuario_app/cadastrar_carona.html', context)

@require_POST
def iniciar_carona(request, carona_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'})
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carona = get_object_or_404(Carona, id=carona_id, motorista=usuario)
    
    if carona.status == 'Agendada':
        carona.status = 'Em Andamento'
        carona.save()
        return JsonResponse({'success': True, 'new_status': 'Em Andamento'})
    
    return JsonResponse({'success': False, 'error': 'Status inválido'})

@require_POST
def finalizar_carona(request, carona_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'})
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carona = get_object_or_404(Carona, id=carona_id, motorista=usuario)
    
    if carona.status == 'Em Andamento':
        carona.status = 'Finalizada'
        carona.save()
        return JsonResponse({'success': True, 'new_status': 'Finalizada'})
    
    return JsonResponse({'success': False, 'error': 'Status inválido'})

@require_POST
def remover_carona(request, carona_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'})
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carona = get_object_or_404(Carona, id=carona_id, motorista=usuario)
    
    if carona.status in ['Agendada', 'Cancelada']:
        carona.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Não é possível remover caronas em andamento ou finalizadas'})

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
    if request.session.get("usuario_id"):
        return redirect("solicitar_carona")

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["password"]
            remember_me = form.cleaned_data["remember_me"]

            try:
                usuario = Usuario.objects.get(email=email)

                if check_password(senha, usuario.senha):
                    request.session["usuario_id"] = usuario.id

                    if remember_me:
                        request.session.set_expiry(1209600)
                    else:
                        request.session.set_expiry(0)

                    return redirect("solicitar_carona")

                # senha errada → erro só no campo password
                form.add_error("password", "Senha incorreta.")

            except Usuario.DoesNotExist:
                # email não existe → erro só no campo email
                form.add_error("email", "Email não encontrado.")

    else:
        form = LoginForm()

    return render(request, "usuario_app/login.html", {
        "form": form
    })



def solicitar_carona(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        return redirect("login")
    
    # Obter parâmetros da busca
    busca = request.GET.get('busca', '').strip()
    data_filtro = request.GET.get('data', '').strip()
    vagas_filtro = request.GET.get('vagas', '').strip()
    tipo_veiculo_filtro = request.GET.get('tipo_veiculo', '').strip()
    campus_filtro = request.GET.get('campus', '').strip()
    
    # DEBUG: Imprimir parâmetros recebidos (remova em produção)
    print(f"DEBUG - Parâmetros recebidos:")
    print(f"  Busca: {busca}")
    print(f"  Data: {data_filtro}")
    print(f"  Vagas: {vagas_filtro}")
    print(f"  Tipo Veículo: {tipo_veiculo_filtro}")
    print(f"  Campus: {campus_filtro}")
    
    # Filtrar caronas.
    caronas_query = Carona.objects.filter(
        status='Agendada'
    ).exclude(
        motorista=usuario
    )
    
    # DEBUG: Ver quantas caronas antes dos filtros
    print(f"DEBUG - Caronas antes dos filtros: {caronas_query.count()}")
    
    # filtro de busca
    if busca:
        caronas_query = caronas_query.filter(
            Q(origem__icontains=busca) | 
            Q(destino__icontains=busca) |
            Q(motorista__nome__icontains=busca)
        )
        print(f"DEBUG - Após busca: {caronas_query.count()}")
    
    # filtro de data
    if data_filtro:
        try:
            # Converter string para date object
            data_obj = datetime.strptime(data_filtro, '%d-%m-%Y').date()
            caronas_query = caronas_query.filter(
                horario_e_data__date=data_obj
            )
            print(f"DEBUG - Após filtro de data {data_filtro}: {caronas_query.count()}")
        except ValueError as e:
            print(f"DEBUG - Erro ao converter data: {e}")
            pass
    
    if vagas_filtro:
        try:
            vagas = int(vagas_filtro)
            caronas_query = caronas_query.filter(vagas_disponiveis__gte=vagas)
            print(f"DEBUG - Após filtro de vagas: {caronas_query.count()}")
        except ValueError:
            print(f"DEBUG - Erro ao converter vagas")
            pass
    
    if tipo_veiculo_filtro:
        caronas_query = caronas_query.filter(veiculo__tipo_veiculo=tipo_veiculo_filtro)
        print(f"DEBUG - Após filtro tipo veículo: {caronas_query.count()}")
    
    if campus_filtro:
        caronas_query = caronas_query.filter(motorista__tipo_campus=campus_filtro)
        print(f"DEBUG - Após filtro campus: {caronas_query.count()}")
    
    caronas_query = caronas_query.order_by('horario_e_data')
    
    # DEBUG: Ver caronas após todos os filtros
    print(f"DEBUG - Caronas após todos os filtros: {caronas_query.count()}")
    
    # Listar todas as caronas para debug
    for carona in caronas_query:
        print(f"DEBUG - Carona: {carona.id} | {carona.origem} -> {carona.destino} | {carona.horario_e_data} | Vagas: {carona.vagas_disponiveis}")
    
    # Preparar dados para template
    caronas_com_status = []
    for carona in caronas_query:
        # Verificar se o usuário já solicitou esta carona
        solicitacao = SolicitacaoCarona.objects.filter(
            carona=carona,
            passageiro=usuario
        ).first()
        
        status_solicitacao = solicitacao.status if solicitacao else None
        
        caronas_com_status.append({
            'carona': carona,
            'status_solicitacao': status_solicitacao
        })
    
    campus_choices = Usuario.TIPO_CAMPUS
    
    filtros_ativos = {
        'busca': busca,
        'data': data_filtro,
        'vagas': vagas_filtro,
        'tipo_veiculo': tipo_veiculo_filtro,
        'campus': campus_filtro,
    }
    
    return render(request, 'usuario_app/solicitar_carona.html', {
        'caronas_com_status': caronas_com_status,
        'usuario': usuario,
        'filtros_ativos': filtros_ativos,
        'campus_choices': campus_choices,
        'tipos_veiculo': [('Carro', 'Carro'), ('Moto', 'Moto')],
    })