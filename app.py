from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'secret-key-alberthzin'
bcrypt = Bcrypt(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'barbearia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# model usuario 
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# model cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# model serviço
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.String(50), nullable=False)

# modelo agendamento
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    cliente = db.relationship('Cliente', backref=db.backref('agendamentos', lazy=True))
    servico = db.relationship('Servico', backref=db.backref('agendamentos', lazy=True))

# rota login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and bcrypt.check_password_hash(usuario.password, password):
            session['username'] = username
            return redirect(url_for('menu_inicial'))
        else:
            flash('Usuário ou senha inválidos!')

    return render_template('login.html')

# rota cadastro de usuários e lista
@app.route('/cadastro-usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if Usuario.query.filter_by(username=username).first():
            flash('Usuário já existe!')
            return redirect(url_for('cadastro_usuario'))

        hashed_password = generate_password_hash(password)

        usuario = Usuario(username=username, password=hashed_password)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('cadastro_usuario'))

    usuarios = Usuario.query.all()
    return render_template('cadastro_usuario.html', usuarios=usuarios)

# rota remover usuario
@app.route('/remover-usuario/<int:id>', methods=['POST'])
def remover_usuario(id):
    if 'username' in session:
        usuario = Usuario.query.get(id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash('Usuário removido com sucesso!')
        else:
            flash('Usuário não encontrado!')

        return redirect(url_for('cadastro_usuario'))
    return redirect(url_for('login'))

# rota menu inicial (somente logado)
@app.route('/menu')
def menu_inicial():
    if 'username' in session:
        return render_template('menu.html', username=session['username'])
    return redirect(url_for('login'))

# rota logout
@app.route('/logout')
def logout():
    session.pop('username', None)
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

#rota cadastro agendamentos
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
    return redirect(url_for('agendamentos_view'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if Usuario.query.count() == 0:
            usuario_admin = Usuario(username='admin', password=bcrypt.generate_password_hash('admin123').decode('utf-8'))
            db.session.add(usuario_admin)
            db.session.commit()

    app.run(debug=True)