from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password,check_password
from .models import Usuario, Veiculo, MensagemChat, Carona,SolicitacaoCarona, Veiculo, Notificacao
from django.contrib import messages
from .forms import CadastroForm,LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import CaronaForm
from django.db.models import Q
from django.utils import timezone
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
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Buscar todas as solicitações do usuário como passageiro
    solicitacoes_passageiro = SolicitacaoCarona.objects.filter(
        passageiro=usuario
    ).select_related(
        'carona', 
        'carona__motorista',
        'carona__veiculo'
    ).order_by('-data_solicitacao')
    
    # Buscar TODAS as caronas do usuário como motorista
    # Incluindo caronas removidas, mas ordenadas por data de criação (mais recentes primeiro)
    caronas_motorista = Carona.objects.filter(
        motorista=usuario
    ).select_related(
        'veiculo'
    ).order_by('-data_criacao')
    
    # Criar uma lista única de eventos, ordenada por data (mais recente primeiro)
    historico_combinado = []
    
    # Adicionar solicitações como passageiro
    for solicitacao in solicitacoes_passageiro:
        carona = solicitacao.carona
        # Verificar se o usuário atual é o motorista que removeu a carona
        motorista_removeu = (carona.status == 'Removida' and carona.motorista == usuario)
        
        historico_combinado.append({
            'tipo': 'solicitacao',
            'objeto': solicitacao,
            'data': solicitacao.data_solicitacao,
            'status': solicitacao.status,
            'carona_status': carona.status,
            'motorista_removeu': motorista_removeu,  # Novo campo
            'carona_motorista_id': carona.motorista.id,  # Para verificar se é o motorista
        })
    
    # Adicionar caronas como motorista
    for carona in caronas_motorista:
        # Para caronas do motorista, ele sempre é quem removeu se o status for Removida
        motorista_removeu = (carona.status == 'Removida')
        
        historico_combinado.append({
            'tipo': 'carona',
            'objeto': carona,
            'data': carona.data_criacao,
            'status': carona.status,
            'carona_status': carona.status,
            'motorista_removeu': motorista_removeu,  # Novo campo
            'carona_motorista_id': carona.motorista.id,  # Sempre será o próprio usuário
        })
    
    # Ordenar por data (mais recente primeiro)
    historico_combinado.sort(key=lambda x: x['data'], reverse=True)
    
    context = {
        'usuario': usuario,
        'historico_combinado': historico_combinado,
    }
    
    return render(request, 'usuario_app/historico.html', context)

@require_POST
def cancelar_solicitacao(request, solicitacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        solicitacao = SolicitacaoCarona.objects.get(
            id=solicitacao_id,
            passageiro=usuario,
            status='Pendente'
        )
    except (Usuario.DoesNotExist, SolicitacaoCarona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Solicitação não encontrada'}, status=404)
    
    # Cancelar a solicitação
    solicitacao.status = 'Recusada'
    solicitacao.save()
    
    # Criar notificação para o motorista
    Notificacao.objects.create(
        usuario=solicitacao.carona.motorista,
        tipo='solicitacao_recusada',
        mensagem=f'{usuario.nome} cancelou a solicitação para a carona até {solicitacao.carona.destino} no dia {solicitacao.carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")}',
        carona=solicitacao.carona,
        solicitacao=solicitacao
    )
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Solicitação cancelada com sucesso!'
    })


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
    
    # Busca caronas do usuário que NÃO estão Finalizadas ou Removidas
    caronas = Carona.objects.filter(
        motorista=usuario
    ).exclude(
        status__in=['Finalizada', 'Removida']
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
        carona.status = 'Removida'
        carona.data_remocao = timezone.now()
        carona.save()
        
        # Recusar automaticamente todas as solicitações pendentes para esta carona
        solicitacoes_pendentes = SolicitacaoCarona.objects.filter(
            carona=carona,
            status='Pendente'
        )
        
        for solicitacao in solicitacoes_pendentes:
            solicitacao.status = 'Recusada'
            solicitacao.save()
            
            # Notificar o passageiro que a carona foi removida
            Notificacao.objects.create(
                usuario=solicitacao.passageiro,
                tipo='solicitacao_recusada',
                mensagem=f'A carona para {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")} foi removida pelo motorista.',
                carona=carona,
                solicitacao=solicitacao
            )
        
        return JsonResponse({'success': True, 'new_status': 'Removida'})
    
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
    
    # VERIFICAR SE O USUÁRIO TEM SOLICITAÇÃO ATIVA 
    solicitacao_ativa = SolicitacaoCarona.objects.filter(
        passageiro=usuario,
        status__in=['Pendente', 'Aceita']
    ).exclude(
        carona__status='Finalizada'  # Exclui solicitações de caronas já finalizadas
    ).first()
    
    tem_solicitacao_ativa = solicitacao_ativa is not None
    
    # Obter parâmetros da busca
    busca = request.GET.get('busca', '').strip()
    data_filtro = request.GET.get('data', '').strip()
    vagas_filtro = request.GET.get('vagas', '').strip()
    tipo_veiculo_filtro = request.GET.get('tipo_veiculo', '').strip()
    campus_filtro = request.GET.get('campus', '').strip()
    
    # Filtrar caronas: status Agendada, excluir as do próprio usuário
    caronas_query = Carona.objects.filter(
        status='Agendada'
    ).exclude(
        motorista=usuario
    )
    
    # Aplicar filtro de busca
    if busca:
        caronas_query = caronas_query.filter(
            Q(origem__icontains=busca) | 
            Q(destino__icontains=busca) |
            Q(motorista__nome__icontains=busca)
        )
    
    # Aplicar filtro de data
    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            caronas_query = caronas_query.filter(
                horario_e_data__date=data_obj
            )
        except ValueError:
            pass
    
    # Aplicar filtro de vagas
    if vagas_filtro:
        try:
            vagas = int(vagas_filtro)
            caronas_query = caronas_query.filter(vagas_disponiveis__gte=vagas)
        except ValueError:
            pass
    
    # Aplicar filtro de tipo de veículo
    if tipo_veiculo_filtro:
        caronas_query = caronas_query.filter(veiculo__tipo_veiculo=tipo_veiculo_filtro)
    
    # Aplicar filtro de campus
    if campus_filtro:
        caronas_query = caronas_query.filter(motorista__tipo_campus=campus_filtro)
    
    # Ordenar por data/horário mais próximo
    caronas_query = caronas_query.order_by('horario_e_data')
    
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
            'status_solicitacao': status_solicitacao,
            'solicitacao_id': solicitacao.id if solicitacao else None,
            'solicitacao_obj': solicitacao  # Passar o objeto completo
        })
    
    # Obter todas as opções de campus
    campus_choices = Usuario.TIPO_CAMPUS
    
    # Calcular estatísticas de filtros ativos
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
        'solicitacao_ativa': solicitacao_ativa,
        'tem_solicitacao_ativa': tem_solicitacao_ativa,
    })



@require_POST
def solicitar_carona_action(request, carona_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        carona = Carona.objects.get(id=carona_id)
    except (Usuario.DoesNotExist, Carona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Carona não encontrada'}, status=404)
    
    # VERIFICAÇÃO CRÍTICA: Passageiro só pode ter UMA solicitação ativa por vez
    # Consideramos "ativa" uma solicitação com status Pendente ou Aceita
    # EXCLUINDO caronas que já foram finalizadas
    solicitacoes_ativas = SolicitacaoCarona.objects.filter(
        passageiro=usuario,
        status__in=['Pendente', 'Aceita']
    ).exclude(
        carona__status='Finalizada'  # Exclui solicitações de caronas já finalizadas
    )
    
    if solicitacoes_ativas.exists():
        # Encontre a solicitação ativa
        solicitacao_ativa = solicitacoes_ativas.first()
        
        # Verificar se é a mesma carona (para atualizar status se necessário)
        if solicitacao_ativa.carona.id == carona_id:
            return JsonResponse({
                'status': 'error', 
                'message': 'Você já solicitou esta carona'
            })
        
        # Se for uma carona diferente, impedir nova solicitação
        status_ativa = solicitacao_ativa.status
        destino_ativa = solicitacao_ativa.carona.destino
        data_ativa = solicitacao_ativa.carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")
        
        mensagem = f'Você já tem uma solicitação {status_ativa.lower()}'
        if status_ativa == 'Aceita':
            mensagem += f' para a carona até {destino_ativa} no dia {data_ativa}.'
        else:
            mensagem += f'. Finalize ou cancele essa solicitação antes de solicitar outra.'
        
        return JsonResponse({
            'status': 'error', 
            'message': mensagem
        })
    
    # Verificar se já existe uma solicitação para esta carona (mesmo que recusada)
    solicitacao_existente = SolicitacaoCarona.objects.filter(
        carona=carona,
        passageiro=usuario
    ).first()
    
    if solicitacao_existente:
        # Se foi recusada, permitir solicitar novamente
        if solicitacao_existente.status == 'Recusada':
            # Atualizar a solicitação existente para Pendente
            solicitacao_existente.status = 'Pendente'
            solicitacao_existente.save()
            
            # Criar notificação para o motorista
            Notificacao.objects.create(
                usuario=carona.motorista,
                tipo='nova_solicitacao',
                mensagem=f'{usuario.nome} solicitou uma vaga na sua carona para {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")}',
                carona=carona,
                solicitacao=solicitacao_existente
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Solicitação reenviada com sucesso!'
            })
        else:
            return JsonResponse({
                'status': 'error', 
                'message': 'Você já solicitou esta carona'
            })
    
    # Verificar se há vagas disponíveis
    if carona.vagas_disponiveis <= 0:
        return JsonResponse({
            'status': 'error', 
            'message': 'Não há vagas disponíveis nesta carona'
        })
    
    # Criar solicitação
    solicitacao = SolicitacaoCarona.objects.create(
        carona=carona,
        passageiro=usuario,
        status='Pendente'
    )
    
    # Criar notificação para o motorista
    Notificacao.objects.create(
        usuario=carona.motorista,
        tipo='nova_solicitacao',
        mensagem=f'{usuario.nome} solicitou uma vaga na sua carona para {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Solicitação enviada com sucesso!'
    })


@require_POST
def aceitar_solicitacao_notificacao(request, notificacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        notificacao = Notificacao.objects.get(id=notificacao_id, usuario=usuario)
        solicitacao = notificacao.solicitacao
        carona = solicitacao.carona
    except (Usuario.DoesNotExist, Notificacao.DoesNotExist, SolicitacaoCarona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)
    
    # Verificar se o usuário é o motorista da carona
    if carona.motorista != usuario:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=403)
    
    # Verificar se ainda há vagas
    if carona.vagas_disponiveis <= 0:
        # Criar notificação de erro para o motorista
        Notificacao.objects.create(
            usuario=usuario,
            tipo='solicitacao_recusada',
            mensagem=f'Não foi possível aceitar a solicitação de {solicitacao.passageiro.nome} - Vagas esgotadas',
            carona=carona,
            solicitacao=solicitacao
        )
        
        # Atualizar solicitação
        solicitacao.status = 'Recusada'
        solicitacao.save()
        
        # Marcar notificação como lida
        notificacao.lida = True
        notificacao.save()
        
        return JsonResponse({
            'status': 'error', 
            'message': 'Vagas esgotadas - Solicitação automaticamente recusada'
        })
    
    # Aceitar solicitação
    solicitacao.status = 'Aceita'
    solicitacao.save()
    
    # Atualizar vagas da carona
    carona.vagas_disponiveis -= 1
    carona.save()
    
    # Criar notificação para o passageiro informando aceitação
    Notificacao.objects.create(
        usuario=solicitacao.passageiro,
        tipo='solicitacao_aceita',
        mensagem=f'Sua solicitação para a carona até {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")} foi ACEITA por {usuario.nome}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    # Marcar notificação original como lida
    notificacao.lida = True
    notificacao.save()
    
    # Criar notificação de confirmação para o motorista
    Notificacao.objects.create(
        usuario=usuario,
        tipo='solicitacao_aceita',
        mensagem=f'Você aceitou a solicitação de {solicitacao.passageiro.nome} para a carona até {carona.destino}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Solicitação aceita com sucesso!'
    })

@require_POST
def recusar_solicitacao_notificacao(request, notificacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        notificacao = Notificacao.objects.get(id=notificacao_id, usuario=usuario)
        solicitacao = notificacao.solicitacao
        carona = solicitacao.carona
    except (Usuario.DoesNotExist, Notificacao.DoesNotExist, SolicitacaoCarona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)
    
    # Verificar se o usuário é o motorista da carona
    if carona.motorista != usuario:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=403)
    
    # Recusar solicitação
    solicitacao.status = 'Recusada'
    solicitacao.save()
    
    # Criar notificação para o passageiro informando recusa
    Notificacao.objects.create(
        usuario=solicitacao.passageiro,
        tipo='solicitacao_recusada',
        mensagem=f'Sua solicitação para a carona até {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")} foi RECUSADA por {usuario.nome}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    # Marcar notificação original como lida
    notificacao.lida = True
    notificacao.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Solicitação recusada'
    })

@require_POST
def passageiro_recusar_carona(request, notificacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        notificacao = Notificacao.objects.get(id=notificacao_id, usuario=usuario)
        solicitacao = notificacao.solicitacao
        carona = solicitacao.carona
    except (Usuario.DoesNotExist, Notificacao.DoesNotExist, SolicitacaoCarona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)
    
    # Verificar se o usuário é o passageiro da solicitação
    if solicitacao.passageiro != usuario:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=403)
    
    # Verificar se a solicitação está aceita
    if solicitacao.status != 'Aceita':
        return JsonResponse({
            'status': 'error', 
            'message': 'Esta solicitação não está aceita'
        })
    
    # Passageiro recusando a carona (após ter sido aceita)
    solicitacao.status = 'Recusada'
    solicitacao.save()
    
    # Devolver a vaga para a carona
    carona.vagas_disponiveis += 1
    carona.save()
    
    # Criar notificação para o motorista informando que o passageiro recusou
    Notificacao.objects.create(
        usuario=carona.motorista,
        tipo='passageiro_recusou',
        mensagem=f'{usuario.nome} recusou a carona para {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    # Marcar notificação original como lida
    notificacao.lida = True
    notificacao.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Você recusou a carona'
    })

@require_POST
def marcar_notificacao_lida(request, notificacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        notificacao = Notificacao.objects.get(id=notificacao_id, usuario=usuario)
    except (Usuario.DoesNotExist, Notificacao.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)
    
    notificacao.lida = True
    notificacao.save()
    
    return JsonResponse({'status': 'success'})

def contador_notificacoes(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'count': 0})
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        count = Notificacao.objects.filter(usuario=usuario, lida=False).count()
        return JsonResponse({'count': count})
    except Usuario.DoesNotExist:
        return JsonResponse({'count': 0})




@require_POST
def motorista_remover_passageiro(request, notificacao_id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        notificacao = Notificacao.objects.get(id=notificacao_id, usuario=usuario)
        solicitacao = notificacao.solicitacao
        carona = solicitacao.carona
    except (Usuario.DoesNotExist, Notificacao.DoesNotExist, SolicitacaoCarona.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)
    
    # Verificar se o usuário é o motorista da carona
    if carona.motorista != usuario:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=403)
    
    # Verificar se a solicitação está aceita
    if solicitacao.status != 'Aceita':
        return JsonResponse({
            'status': 'error', 
            'message': 'Esta solicitação não está aceita'
        })
    
    # Motorista removendo o passageiro
    passageiro_nome = solicitacao.passageiro.nome
    
    # Devolver a vaga para a carona
    carona.vagas_disponiveis += 1
    carona.save()
    
    # Atualizar status da solicitação
    solicitacao.status = 'Recusada'
    solicitacao.save()
    
    # Criar notificação para o passageiro informando que foi removido
    Notificacao.objects.create(
        usuario=solicitacao.passageiro,
        tipo='solicitacao_recusada',
        mensagem=f'O motorista {usuario.nome} removeu você da carona para {carona.destino} no dia {carona.horario_e_data.strftime("%d/%m/%Y às %H:%M")}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    # Marcar notificação original como lida
    notificacao.lida = True
    notificacao.save()
    
    # Criar notificação de confirmação para o motorista
    Notificacao.objects.create(
        usuario=usuario,
        tipo='solicitacao_recusada',
        mensagem=f'Você removeu {passageiro_nome} da carona para {carona.destino}',
        carona=carona,
        solicitacao=solicitacao
    )
    
    return JsonResponse({
        'status': 'success', 
        'message': f'Passageiro {passageiro_nome} removido com sucesso!'
    })