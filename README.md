
# BARBO - Aplicação para Cabelereiros (EM CONSTRUÇÃO)

O Barbo é um sistema para auxiliar cabelereiros nos agendamentos, cadastros, registros de clientes, serviços e usuários.


## Rodando localmente

Clone o projeto

```bash
  git clone https://github.com/asmnery/barbo-app-v2
```

Instale as dependências

```bash
  pip install -r requirements.txt
```

Inicie o servidor

```bash
  python app.py
```


## Variáveis de Ambiente

Para rodar esse projeto, você vai precisar adicionar as seguintes variáveis de ambiente no seu .env

`SECRET_KEY`

`SQLALCHEMY_DATABASE_URI`

`AUTH_TOKEN`

`ACCOUNT_SID`

`TWILIO_PHONE_NUMBER`


## Funcionalidades

- Criação de clientes, serviços prestados e usários (funcionários)
- Agendamento de horários
- Notificação via SMS 24h antes do horário agendado
- Níveis de privilégio para funcionalidades específicas


## Stack utilizada

**Front-end:** HTML, CSS, Javascript

**Back-end:** Python, Flask

**Banco de Dados:** MySQL


## Autores

- [@asmnery](https://www.github.com/asmnery)

