from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
import bcrypt
from credentials import settings, credenciais


app = Flask("Farmacia")
app.secret_key = 'deena'  # Substitua por uma chave secreta forte.
app.config["MONGO_URI"] = f"mongodb+srv://{credenciais['user_mongo']}:{credenciais['password_mongo']}@{settings['host']}/{settings['database']}?retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route('/')
def home():
    if 'username' in session:
        return f'Bem-vindo, {session["username"]}! <a href="/logout">Sair</a>'
    return 'Página inicial - <a href="/login">Login</a>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        users = mongo.db.usuarios
        users.insert_one({'username': username})
        session['username'] = username
        return redirect(url_for('home')), 201
    return 'Formulário de Registro'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        users = mongo.db.usuarios
        user = users.find_one({'username': username})
        if username:
            session['username'] = username
            return redirect(url_for('home')), 200
        return 'Usuário não encontrado!', 404
    return 'Formulário de Login'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'GET':
        produtos = list(mongo.db.produtos.find({},{'marca_produto':1, 'nome_produto':1, 'descricao_produto':1, 'quantidade_por_unidade_produto':1, 'notificacao_baixo_estoque_produto':1, '_id':0}))
        produtos_list = [{"Marca":produto['marca_produto'], "Nome":produto['nome_produto'], "Descrição":produto['descricao_produto'], "Quantidade por Unidade":produto['quantidade_por_unidade_produto'], "Notificação de Baixo Estoque":produto['notificacao_baixo_estoque_produto']} for produto in produtos]
        return jsonify({"Produtos":produtos_list}), 200
    
    elif request.method == 'POST':
        try:
            request_data = request.form

            if 'marca_produto' not in request_data:
                return {'ERRO': 'marca do produto não informada'}, 400
            marca_produto = request_data.get('marca_produto')
            
            if 'nome_produto' not in request_data:
                return {'ERRO': 'nome do produto não informado'}, 400
            nome_produto = request_data.get('nome_produto')
            
            if 'descricao_produto' not in request_data: 
                return {'ERRO': 'descrição do produto não informada'}, 400
            descricao_produto = request_data.get('descricao_produto')
            
            if 'quantidade_por_unidade_produto' not in request_data:
                return {'ERRO': 'quantidade por unidade do produto não informada'}, 400
            quantidade_por_unidade_produto = request_data.get('quantidade_por_unidade_produto')
            
            if 'notificacao_baixo_estoque_produto' not in request_data:
                return {'ERRO': 'notificação de baixo estoque do produto não informada'}, 400
            notificacao_baixo_estoque_produto = int(request_data.get('notificacao_baixo_estoque_produto'))
            
            data_produto_novo = {'marca_produto': marca_produto, 'nome_produto': nome_produto, 'descricao_produto': descricao_produto, 'quantidade_por_unidade_produto': quantidade_por_unidade_produto, 'notificacao_baixo_estoque_produto': notificacao_baixo_estoque_produto}
            
            mongo.db.produtos.insert_one(data_produto_novo)
            return {"SUCESSO" :'Produto Adicionado com sucesso!'}, 201
        
        except:
            return {'ERRO': 'Erro ao tentar adicionar produto na base de dados'}, 500




if __name__ == '__main__':
    app.run(debug=True)