let btnAdicionarCarona, popupOverlay, btnFecharPopup, btnCancelar, caronaForm, listaCaronas, horarioInput;

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    inicializarElementos();
    configurarEventos();
});

// Inicializar referências aos elementos DOM
function inicializarElementos() {
    btnAdicionarCarona = document.getElementById('btnAdicionarCarona');
    popupOverlay = document.getElementById('popupOverlay');
    btnFecharPopup = document.getElementById('btnFecharPopup');
    btnCancelar = document.getElementById('btnCancelar');
    caronaForm = document.getElementById('caronaForm');
    listaCaronas = document.getElementById('listaCaronas');
    horarioInput = document.getElementById('horario');
}

// Configurar todos os event listeners
function configurarEventos() {
    // Mostrar pop-up
    btnAdicionarCarona.addEventListener('click', mostrarPopup);
    
    // Fechar pop-up
    btnFecharPopup.addEventListener('click', fecharPopup);
    btnCancelar.addEventListener('click', fecharPopup);
    
    // Fechar pop-up clicando no overlay
    popupOverlay.addEventListener('click', function(e) {
        if (e.target === popupOverlay) {
            fecharPopup();
        }
    });
    
    // Fechar pop-up com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !popupOverlay.classList.contains('hidden')) {
            fecharPopup();
        }
    });
    
    // Submeter formulário
    caronaForm.addEventListener('submit', function(e) {
        e.preventDefault();
        processarFormulario();
    });
}

// Mostrar pop-up do formulário
function mostrarPopup() {
    popupOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Fechar pop-up do formulário
function fecharPopup() {
    popupOverlay.classList.add('hidden');
    document.body.style.overflow = 'auto';
    caronaForm.reset();
}

// Processar envio do formulário
function processarFormulario() {
    const horario = document.getElementById('horario').value;
    const origem = document.getElementById('origem').value;
    const destino = document.getElementById('destino').value;
    
    if (horario && origem && destino) {
        const horarioFormatado = formatarHorario(horario);
        const novaCarona = criarCardCarona(horarioFormatado, origem, destino);
        
        listaCaronas.insertBefore(novaCarona, listaCaronas.firstChild);
        fecharPopup();
        mostrarMensagem('Carona criada com sucesso!', 'success');
    }
}

// Formatar horário 24h para AM/PM
function formatarHorario(horario24h) {
    const [horas, minutos] = horario24h.split(':');
    const hora = parseInt(horas);
    const periodo = hora >= 12 ? 'PM' : 'AM';
    const hora12 = hora % 12 || 12;
    return `${hora12}:${minutos} ${periodo}`;
}

// Criar novo card de carona
function criarCardCarona(horario, origem, destino) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-xl shadow-md border border-gray-100';
    card.innerHTML = `
        <div class="p-6">
            <!-- Horário -->
            <div class="flex items-center justify-between mb-6">
                <span class="text-xl font-semibold text-gray-800">${horario}</span>
                <!-- Ícone do veículo -->
                <div class="flex items-center gap-2 text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                    </svg>
                </div>
            </div>

            <div class="mb-6 space-y-3">
                <div class="space-y-1">
                    <p class="text-gray-500 font-medium min-w-12">Origem</p>
                    <p class="text-gray-800">${origem}</p>
                </div>
                <div class="space-y-1">
                    <p class="text-gray-500 font-medium min-w-12">Destino</p>
                    <p class="text-gray-800">${destino}</p>
                </div>
            </div>

            <!-- Motorista -->
            <div class="flex items-center mb-6">
                <div class="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold mr-4 text-lg">
                    V
                </div>
                <div class="font-medium text-gray-800 text-lg">
                    Você
                </div>
            </div>

            <!-- Botões -->
            <div class="flex gap-4">
                <button class="flex-1 bg-red-500 hover:bg-red-600 text-white py-3 px-4 rounded-lg font-medium transition-colors text-base deletar-carona">
                    Deletar
                </button>
                <button class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded-lg font-medium transition-colors text-base iniciar-carona">
                    Iniciar
                </button>
            </div>
        </div>
    `;

    // Adicionar eventos aos botões do novo card
    const btnDeletar = card.querySelector('.deletar-carona');
    const btnIniciar = card.querySelector('.iniciar-carona');

    btnDeletar.addEventListener('click', function() {
        if (confirm('Tem certeza que deseja deletar esta carona?')) {
            card.remove();
            mostrarMensagem('Carona deletada!', 'error');
        }
    });

    btnIniciar.addEventListener('click', function() {
        btnIniciar.textContent = 'Em andamento';
        btnIniciar.classList.remove('bg-blue-500', 'hover:bg-blue-600');
        btnIniciar.classList.add('bg-green-500', 'hover:bg-green-600', 'cursor-default');
        btnDeletar.textContent = 'Finalizar';
        btnDeletar.classList.remove('bg-red-500', 'hover:bg-red-600');
        btnDeletar.classList.add('bg-gray-500', 'hover:bg-gray-600');
        mostrarMensagem('Carona iniciada!', 'success');
    });

    return card;
}

// Função para mostrar mensagens (pode ser expandida para notificações visuais)
function mostrarMensagem(mensagem, tipo) {
    console.log(`${tipo}: ${mensagem}`);
    // Aqui você pode implementar um sistema de notificações toast
    // Exemplo: criar um elemento de notificação e adicionar ao DOM
}