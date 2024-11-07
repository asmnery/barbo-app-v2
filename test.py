import schedule
import time
from datetime import datetime
from twilio.rest import Client
import mysql.connector

# Configurações da conta Twilio
ACCOUNT_SID = "AC58da603dfd219cad57a785a5bc3e1dae"
AUTH_TOKEN = "90fab39bc27df2bfa3343c98ed2280de"
TWILIO_PHONE_NUMBER = "+12512195143"

# Configurações do banco de dados MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "barbo_db"
}

# Função para enviar SMS
def enviar_sms(to_number, mensagem):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=mensagem,
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )
    print(f"Mensagem enviada para {to_number}: {mensagem}")

# Função para consultar o horário do banco de dados
def obter_dados_notificacao():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT horario, numero_telefone, mensagem FROM notificacoes WHERE enviada = 0")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        return []

# Função para enviar a notificação quando o horário chegar
def agendar_notificacoes():
    dados_notificacao = obter_dados_notificacao()
    for horario, numero_telefone, mensagem in dados_notificacao:
        if datetime.now().strftime("%H:%M") == horario.strftime("%H:%M"):
            enviar_sms(numero_telefone, mensagem)
            marcar_notificacao_enviada(horario, numero_telefone)

# Função para marcar a notificação como enviada no banco
def marcar_notificacao_enviada(horario, numero_telefone):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "UPDATE notificacoes SET enviada = 1 WHERE horario = %s AND numero_telefone = %s"
        cursor.execute(query, (horario, numero_telefone))
        conn.commit()
        conn.close()
        print(f"Notificação marcada como enviada para {numero_telefone} no horário {horario}.")
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o banco de dados: {err}")

# Configura para verificar notificações a cada minuto
schedule.every().minute.do(agendar_notificacoes)

# Loop principal para manter o agendamento em execução
while True:
    schedule.run_pending()
    time.sleep(1)
