from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Página inicial (Menu)
@app.route('/')
def index():
    return render_template('index.html')

# Página de agendamentos
@app.route('/agendamentos')
def agendamentos():
    return render_template('agendamentos.html')

# Página de cadastro de clientes
@app.route('/cadastro-clientes')
def cadastro_clientes():
    return render_template('cadastro_clientes.html')

# Página de cadastro de serviços
@app.route('/cadastro-servicos')
def cadastro_servicos():
    return render_template('cadastro_servicos.html')

# Rota para receber cadastro de cliente via POST
@app.route('/api/cadastro-cliente', methods=['POST'])
def cadastrar_cliente():
    dados = request.json
    # Aqui você salvaria os dados no banco de dados
    return jsonify({'message': 'Cliente cadastrado com sucesso!'})

# Rota para receber cadastro de serviço via POST
@app.route('/api/cadastro-servico', methods=['POST'])
def cadastrar_servico():
    dados = request.json
    # Aqui você salvaria os dados no banco de dados
    return jsonify({'message': 'Serviço cadastrado com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)