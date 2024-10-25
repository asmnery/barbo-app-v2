// Exibir mensagens de erro ou sucesso
document.addEventListener("DOMContentLoaded", function() {
  const flashMessage = document.querySelector('.flash');
  if (flashMessage) {
      setTimeout(() => {
          flashMessage.style.display = 'none';
      }, 3000); // Oculta a mensagem após 3 segundos
  }

  // Validação simples para o formulário de agendamentos
  const agendamentosForm = document.getElementById('agendamentosForm');
  if (agendamentosForm) {
      agendamentosForm.addEventListener('submit', function(event) {
          const cliente = document.getElementById('cliente').value;
          const servico = document.getElementById('servico').value;
          const data = document.getElementById('data').value;

          if (!cliente || !servico || !data) {
              event.preventDefault();
              alert('Por favor, preencha todos os campos do formulário!');
          }
      });
  }
});
