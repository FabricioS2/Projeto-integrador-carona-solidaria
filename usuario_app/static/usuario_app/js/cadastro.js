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

    // 3. Conecta a função ao evento 'change' (mudança de seleção) nos rádios
    radioPerfis.forEach(radio => {
        radio.addEventListener('change', toggleCamposVeiculo);
    });

    // 4. Garante que a função é executada uma vez no carregamento da página
    // Isso define o estado inicial (como "Passageiro" está 'checked' no HTML, ele deve estar escondido)
    toggleCamposVeiculo();
});