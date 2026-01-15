let btnAdicionarCarona, popupOverlay, btnFecharPopup, btnCancelar, caronaForm, listaCaronas;

document.addEventListener('DOMContentLoaded', function () {
    inicializarElementos();
    configurarEventos();
});

function inicializarElementos() {
    btnAdicionarCarona = document.getElementById('btnAdicionarCarona');
    popupOverlay = document.getElementById('popupOverlay');
    btnFecharPopup = document.getElementById('btnFecharPopup');
    btnCancelar = document.getElementById('btnCancelar');
    caronaForm = document.getElementById('caronaForm');
    listaCaronas = document.getElementById('listaCaronas');
}

// Configura eventos
function configurarEventos() {
    btnAdicionarCarona.addEventListener('click', mostrarPopup);
    btnFecharPopup.addEventListener('click', fecharPopup);
    btnCancelar.addEventListener('click', fecharPopup);

    popupOverlay.addEventListener('click', function (e) {
        if (e.target === popupOverlay) fecharPopup();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') fecharPopup();
    });

    caronaForm.addEventListener('submit', function (e) {
        e.preventDefault();
        processarFormulario();
    });
}

function mostrarPopup() {
    popupOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function fecharPopup() {
    popupOverlay.classList.add('hidden');
    document.body.style.overflow = 'auto';
    caronaForm.reset();
}


// Converte 24h → AM/PM
function formatarHorario(h) {
    const [hh, mm] = h.split(":");
    const hNum = parseInt(hh);
    const periodo = hNum >= 12 ? "PM" : "AM";
    const hora12 = hNum % 12 || 12;
    return `${hora12}:${mm} ${periodo}`;
}

// static/usuario_app/js/cadastrar_carona.js
document.addEventListener('DOMContentLoaded', function() {
    const btnAdicionarCarona = document.getElementById('btnAdicionarCarona');
    const popupOverlay = document.getElementById('popupOverlay');
    const btnFecharPopup = document.getElementById('btnFecharPopup');
    const btnCancelar = document.getElementById('btnCancelar');
    const caronaForm = document.getElementById('caronaForm');
    const listaCaronas = document.getElementById('listaCaronas');

    // Abrir popup
    btnAdicionarCarona.addEventListener('click', function() {
        popupOverlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    });

    // Fechar popup
    function fecharPopup() {
        popupOverlay.classList.add('hidden');
        document.body.style.overflow = 'auto';
        caronaForm.reset();
    }

    btnFecharPopup.addEventListener('click', fecharPopup);
    btnCancelar.addEventListener('click', fecharPopup);

    // Fechar ao clicar fora do popup
    popupOverlay.addEventListener('click', function(e) {
        if (e.target === popupOverlay) {
            fecharPopup();
        }
    });

    // Enviar formulário via AJAX
    caronaForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || 'Carona criada com sucesso!');
                fecharPopup();
                location.reload(); // Recarrega a página para mostrar a nova carona
            } else {
                // Mostrar erros de validação
                if (data.errors) {
                    let errorMessage = 'Erro ao criar carona:\n';
                    for (const field in data.errors) {
                        errorMessage += `${field}: ${data.errors[field].join(', ')}\n`;
                    }
                    alert(errorMessage);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao criar carona. Tente novamente.');
        });
    });
});

// Funções para manipular caronas
function iniciarCarona(caronaId) {
    if (!confirm('Deseja iniciar esta carona?')) return;
    
    fetch(`/caronas/${caronaId}/iniciar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Carona iniciada com sucesso!');
            location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    });
}

function finalizarCarona(caronaId) {
    if (!confirm('Deseja finalizar esta carona?')) return;
    
    fetch(`/caronas/${caronaId}/finalizar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Carona finalizada com sucesso!');
            location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    });
}

function removerCarona(caronaId) {
    if (!confirm('Deseja remover esta carona?')) return;
    
    fetch(`/caronas/${caronaId}/remover/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Carona removida com sucesso!');
            location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    });
}

// Função auxiliar para pegar o token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}