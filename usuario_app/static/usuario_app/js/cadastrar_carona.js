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
/*
// Cria o card da carona
function criarCardCarona({ horario, origem, destino }) {
    const card = document.createElement("div");
    card.className = "bg-white rounded-xl shadow-md ride-card p-4 flex flex-col space-y-3";

    card.innerHTML = `
        <div class="flex justify-between items-center pb-2 border-b border-gray-100">
            <div class="flex items-center space-x-2 text-sm font-medium text-gray-700">
                <svg class="w-5 h-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"><circle cx="12" cy="7" r="4"></circle></svg>
                <span>Usuário...</span>
            </div>
            <p class="text-sm font-semibold text-gray-700">${horario}</p>
        </div>

        <div class="flex items-start space-x-3">
            <div class="flex-1">
                <p class="text-gray-500">De:</p>
                <div class="py-2"><span class="text-gray-800 font-medium">${origem}</span></div>

                <p class="text-gray-500">Para:</p>
                <div class="py-2"><span class="text-gray-800 font-medium">${destino}</span></div>
            </div>
        </div>

        <div class="flex justify-end space-x-2 pt-3 border-t border-gray-100">
            <button class="btn-remover bg-red-500 hover:bg-red-600 text-white px-4 py-1 rounded-lg text-sm">Remover</button>
            <button class="btn-iniciar bg-blue-500 hover:bg-blue-600 text-white px-4 py-1 rounded-lg text-sm">Iniciar</button>
        </div>
    `;

    const btnRemover = card.querySelector(".btn-remover");
    const btnIniciar = card.querySelector(".btn-iniciar");

    // Remover o card
    btnRemover.addEventListener("click", () => {
        card.remove();
        mostrarMensagem("Carona removida!", "error");
    });

    // INICIAR CARONA
    btnIniciar.addEventListener("click", () => {
        if (btnIniciar.textContent === "Iniciar") {

            // Muda o botão Iniciar → Em andamento (verde)
            btnIniciar.textContent = "Em andamento";
            btnIniciar.classList.remove("bg-blue-500", "hover:bg-blue-600");
            btnIniciar.classList.add("bg-green-600");

            // Substitui botão Remover → Finalizar (amarelo)
            btnRemover.textContent = "Finalizar";
            btnRemover.classList.remove("bg-red-500", "hover:bg-red-600");
            btnRemover.classList.add("bg-yellow-500", "hover:bg-yellow-600");

            // Ajusta ação do novo botão Finalizar
            btnRemover.onclick = () => {
                card.remove();
                mostrarMensagem("Carona finalizada!", "success");
            };

            mostrarMensagem("Carona iniciada!", "success");
        }
    });

    return card;
} 
    */