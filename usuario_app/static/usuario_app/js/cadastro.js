document.addEventListener('DOMContentLoaded', function() {
    // 1. Seleciona os elementos de interesse
    // Seleciona todos os botões de rádio que têm o atributo name="perfil"
    const radioPerfis = document.querySelectorAll('input[name="perfil"]');
    
    // Seleciona o bloco de campos de veículo que queremos esconder/mostrar
    // A ID 'camposVeiculo' foi definida no HTML
    const camposVeiculo = document.getElementById('camposVeiculo');
    // 2. Define a função que aplica a lógica (mostrar ou esconder)
    function toggleCamposVeiculo() {
        // Verifica se a opção "Motorista" está marcada
        // A ID 'perfilMotorista' foi definida no HTML
        const isMotorista = document.getElementById('perfilMotorista').checked;

        if (isMotorista) {
            // Se for Motorista:
            // a) Mostra o bloco de campos do veículo
            camposVeiculo.style.display = 'block';
            
            // b) Torna os campos de veículo obrigatórios (para validação)
            camposVeiculo.querySelectorAll('input').forEach(input => {
                // Remove a exigência de ser obrigatório apenas para o campo 'cor'
                if (input.id !== 'cor') { 
                    input.setAttribute('required', 'required');
                }
            });
            
        } else {
            // Se for Passageiro:
            // a) Esconde o bloco de campos do veículo
            camposVeiculo.style.display = 'none';
            
            // b) Remove a obrigatoriedade dos campos escondidos
            camposVeiculo.querySelectorAll('input').forEach(input => {
                input.removeAttribute('required');
                // Dica: Limpar o valor do campo evita envio de dados indesejados no POST
                input.value = ''; 
            });
        }
    }
    function formatarCPF(campo) {
    // 1. Remove tudo que não for dígito.
    let valor = campo.value.replace(/\D/g, "");

    // 2. Limita a 11 dígitos, que são os dígitos do CPF.
    if (valor.length > 11) {
        valor = valor.substring(0, 11);
    }

    // 3. Aplica a máscara (do mais longo para o mais curto)
    
    // NNN.NNN.NNN-NN
    if (valor.length === 11) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, "$1.$2.$3-$4");
    } 
    // NNN.NNN.NNN
    else if (valor.length > 6) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})/, "$1.$2.$3");
    } 
    // NNN.NNN
    else if (valor.length > 3 ) {
        valor = valor.replace(/^(\d{3})(\d{3})/, "$1.$2");
    }

    // 4. Atribui o novo valor formatado ao campo.
    campo.value = valor;
}
    // 3. Conecta a função ao evento 'change' (mudança de seleção) nos rádios
    radioPerfis.forEach(radio => {
        radio.addEventListener('change', toggleCamposVeiculo);
    });

    // 4. Garante que a função é executada uma vez no carregamento da página
    // Isso define o estado inicial (como "Passageiro" está 'checked' no HTML, ele deve estar escondido)
    toggleCamposVeiculo();
});


    function formatarCPF(campo) {
    // 1. Remove TUDO que não é dígito para trabalhar apenas com os 11 números
    let valor = campo.value.replace(/\D/g, ""); 

    // 2. Limita a string de DÍGITOS a no máximo 11. 
    // Isso deve ser mantido, pois o CPF tem 11 números.
    if (valor.length > 11) {
        valor = valor.substring(0, 11);
    }

    // 3. Aplica a formatação condicionalmente

    // Formato completo 000.000.000-00 (11 dígitos)
    if (valor.length > 9) {
        // Usa $1.$2.$3-$4 para capturar os 4 grupos e inserir o hífen
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, "$1.$2.$3-$4");
    } 
    // Formato 000.000.000 (9 dígitos)
    else if (valor.length > 6) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})$/, "$1.$2.$3");
    } 
    // Formato 000.000 (6 dígitos)
    else if (valor.length > 3) {
        valor = valor.replace(/^(\d{3})(\d{3})$/, "$1.$2");
    } 
    // Se for 3 dígitos ou menos, fica sem formatação (apenas os números)

    // 4. Atribui o valor formatado de volta ao campo
    campo.value = valor;
}

   function togglePasswordVisibility() {
    // 1. Elementos essenciais:
    // O campo de input (ID="password")
    const passwordField = document.getElementById('password'); 
    // O SPAN com o ícone (dentro do botão com ID="toggle-password")
    const toggleIcon = document.getElementById('toggle-password').querySelector('.material-symbols-outlined'); 
    
    // LINHA DE DIAGNÓSTICO: Verifique se esses elementos estão sendo encontrados
    console.log("Campo Senha:", passwordField);
    console.log("Ícone:", toggleIcon);

    if (!passwordField || !toggleIcon) {
        console.error("ERRO: Elemento HTML 'password' ou 'toggle-password' não encontrado.");
        return; // Sai da função se não encontrar os elementos
    }

    if (passwordField.type === 'password') {
        // Altera para 'text' (mostrar senha)
        passwordField.type = 'text'; 
        toggleIcon.textContent = 'visibility_off'; // Muda o ícone
    } else {
        // Altera para 'password' (ocultar senha)
        passwordField.type = 'password'; 
        toggleIcon.textContent = 'visibility'; // Volta o ícone
    }
}