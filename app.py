from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'secret-key-alberthzin'
bcrypt = Bcrypt(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/barbo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações da conta Twilio
ACCOUNT_SID = "*****"
AUTH_TOKEN = "*****"
TWILIO_PHONE_NUMBER = "*****"

db = SQLAlchemy(app)
scheduler = BackgroundScheduler()

# Modelos de Banco de Dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='usuario')

    def __init__(self, username, password, role='usuario'):
        self.username = username
        self.password = password
        self.role = role

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    notificado = db.Column(db.Boolean, default=False)

    cliente = db.relationship('Cliente', backref=db.backref('agendamentos', lazy=True))
    servico = db.relationship('Servico', backref=db.backref('agendamentos', lazy=True))

# função para enviar SMS via Twilio
def enviar_sms(to_number, mensagem):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=mensagem,
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )
    print(f"SMS enviado para {to_number}")

# função para verificar e enviar notificações
def verificar_agendamentos():
    with app.app_context():
        agora = datetime.now()
        agendamentos = Agendamento.query.filter(
            Agendamento.data == agora.date(),
            Agendamento.hora <= (agora + timedelta(minutes=5)).time()
        ).all()

        for agendamento in agendamentos:
            cliente = agendamento.cliente
            servico = agendamento.servico

            # monta a mensagem de notificação
            mensagem = f"Olá {cliente.nome}, lembrete: você tem um {servico.nome_servico} agendado para hoje às {agendamento.hora}."

            # envia o SMS
            enviar_sms(cliente.telefone, mensagem)

            # marca como notificado para evitar notificações duplicadas
            agendamento.notificado = True
            db.session.commit()

# rota login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and bcrypt.check_password_hash(usuario.password, password):
            session['username'] = username
            session['role'] = usuario.role
            return redirect(url_for('menu_inicial'))
        else:
            flash('Usuário ou senha inválidos!')

    return render_template('login.html')

#cadastrar usuarios
@app.route('/cadastro-usuarios', methods=['GET', 'POST'])
def cadastro_usuario():
    if 'username' in session and 'role' in session and session['role'] == 'ADMIN':  # verifica se é admin
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if Usuario.query.filter_by(username=username).first():
                flash('Usuário já existe!')
                return redirect(url_for('cadastro_usuario'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            usuario = Usuario(username=username, password=hashed_password, role='barbeiro')  # definindo o papel

            db.session.add(usuario)
            db.session.commit()

            return redirect(url_for('cadastro_usuario'))

        usuarios = Usuario.query.all()
        return render_template('cadastro_usuarios.html', usuarios=usuarios)    
    return redirect(url_for('login'))


# rota para o menu inicial (somente logado)
@app.route('/menu')
def menu_inicial():
    if 'username' in session:
        usuario = Usuario.query.filter_by(username=session['username']).first()
        if usuario:
            return render_template('menu.html', username=session['username'], role=usuario.role)
    return redirect(url_for('login'))



# rota para logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)  # remove o papel do usuário
    return redirect(url_for('login'))

# rota cadastro clientes
@app.route('/cadastro-clientes', methods=['GET', 'POST'])
def cadastro_clientes():
    if 'username' in session:
        if request.method == 'POST':
            nome = request.form['nome']
            telefone = request.form['telefone']
            email = request.form['email']

            # add cliente ao bd
            cliente = Cliente(nome=nome, telefone=telefone, email=email)
            db.session.add(cliente)
            db.session.commit()

            flash('Cliente cadastrado com sucesso!')
            return redirect(url_for('cadastro_clientes'))

        return render_template('cadastro_clientes.html')
    return redirect(url_for('login'))

# rota cadastro servicos
@app.route('/cadastro-servicos', methods=['GET', 'POST'])
def cadastro_servicos():
    if 'username' in session:
        if request.method == 'POST':
            nome_servico = request.form['nome_servico']
            preco = request.form['preco']

            # add servico ao bd
            servico = Servico(nome_servico=nome_servico, preco=preco)
            db.session.add(servico)
            db.session.commit()

            flash('Serviço cadastrado com sucesso!')
            return redirect(url_for('cadastro_servicos'))

        return render_template('cadastro_servicos.html')
    return redirect(url_for('login'))

# rota cadastro agendamentos
@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos_view():
    if 'username' in session:
        clientes = Cliente.query.all()
        servicos = Servico.query.all()

        if request.method == 'POST':
            cliente_id = request.form['cliente']
            servico_id = request.form['servico']
            data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
            hora = datetime.strptime(request.form['hora'], '%H:%M').time()

            # cria e salva o novo agendamento com data e hora
            agendamento = Agendamento(cliente_id=cliente_id, servico_id=servico_id, data=data, hora=hora)
            db.session.add(agendamento)
            db.session.commit()

            return redirect(url_for('agendamentos_view'))

        # busca todos agendamentos
        agendamentos = db.session.query(
            Agendamento.id,
            Cliente.nome.label('cliente_nome'),
            Servico.nome_servico,
            Servico.preco,
            Agendamento.data,
            Agendamento.hora
        ).join(Cliente, Agendamento.cliente_id == Cliente.id)\
         .join(Servico, Agendamento.servico_id == Servico.id)\
         .all()

        return render_template(
            'agendamentos.html',
            clientes=clientes,
            servicos=servicos,
            agendamentos=agendamentos
        )
    return redirect(url_for('login'))

# rota para excluir um agendamento especifico
@app.route('/delete_agendamento/<int:agendamento_id>', methods=['POST'])
def delete_agendamento(agendamento_id):
    if 'username' in session:
        agendamento = Agendamento.query.get(agendamento_id)
        if agendamento:
            db.session.delete(agendamento)
            db.session.commit()
            flash('Agendamento removido com sucesso!')
    return redirect(url_for('agendamentos_view'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    scheduler.add_job(verificar_agendamentos, 'interval', minutes=1)
    scheduler.start()

    try:
        app.run(debug=True)
    finally:
        scheduler.shutdown()