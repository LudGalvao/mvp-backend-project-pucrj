from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime, date
import os
import json
import asyncio
import httpx
from functools import wraps
import hashlib
import random

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db = SQLAlchemy(app)
CORS(app)

# Configuração do Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Fitness API - Sistema de Usuários e Exercícios"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Modelo de Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=True)
    altura = db.Column(db.Float, nullable=True)
    nivel_experiencia = db.Column(db.String(20), nullable=False, default='iniciante')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    total_exercicios = db.Column(db.Integer, default=0)
    ativo = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'idade': self.idade,
            'peso': self.peso,
            'altura': self.altura,
            'nivel_experiencia': self.nivel_experiencia,
            'data_cadastro': self.data_cadastro.isoformat(),
            'ultimo_acesso': self.ultimo_acesso.isoformat(),
            'total_exercicios': self.total_exercicios,
            'ativo': self.ativo
        }

# Modelo de Exercícios Personalizados
class ExercicioPersonalizado(db.Model):
    __tablename__ = 'exercicios_personalizados'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    vantagens = db.Column(db.Text, nullable=False)
    passo_a_passo = db.Column(db.Text, nullable=False)
    nivel_dificuldade = db.Column(db.String(20), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    concluido = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'vantagens': self.vantagens,
            'passo_a_passo': self.passo_a_passo,
            'nivel_dificuldade': self.nivel_dificuldade,
            'data_criacao': self.data_criacao.isoformat(),
            'concluido': self.concluido,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None
        }

# Exercícios permitidos
EXERCICIOS_PERMITIDOS = [
    "Polichinelo", "Agachamento livre", "Prancha", "Flexão de braço",
    "Abdominal", "Caminhada", "Alongamento", "Afundo", "Mountain climber",
    "Burpee", "Stiff", "Elevação de quadril", "Pular corda", "Step-up",
    "Flexão diamante", "Agachamento sumô", "Saltos laterais", "Prancha lateral"
]

# Configuração da IA
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Função para gerar exercício com IA
async def gerar_exercicio_com_ia(nome_exercicio, nivel_usuario="iniciante"):
    """Gera descrição, vantagens e passo a passo do exercício usando IA"""
    if not OPENROUTER_API_KEY:
        # Fallback se não houver chave da API
        return {
            "descricao": f"Exercício {nome_exercicio} para fortalecimento e condicionamento físico.",
            "vantagens": "Melhora força, resistência, coordenação e saúde cardiovascular.",
            "passo_a_passo": "1. Posicione-se adequadamente. 2. Execute o movimento com controle. 3. Mantenha respiração constante."
        }
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "microsoft/phi-3-mini-4k-instruct",
        "messages": [
            {"role": "system", "content": f"Especialista fitness. Adapte para nível {nivel_usuario}."},
            {"role": "user", "content": f"Descreva o exercício '{nome_exercicio}' para nível {nivel_usuario}: descrição, vantagens e 3 passos."}
        ],
        "max_tokens": 150,
        "temperature": 0.3
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            resposta = response.json()
            conteudo = resposta["choices"][0]["message"]["content"].strip()
            
            # Parsear resposta da IA
            linhas = conteudo.split('\n')
            descricao = linhas[0] if linhas else f"Exercício {nome_exercicio}"
            vantagens = linhas[1] if len(linhas) > 1 else "Benefícios para saúde e fitness"
            passo_a_passo = '\n'.join(linhas[2:]) if len(linhas) > 2 else "1. Posicione-se adequadamente. 2. Execute o movimento. 3. Repita conforme orientação."
            
            return {
                "descricao": descricao,
                "vantagens": vantagens,
                "passo_a_passo": passo_a_passo
            }
    except Exception as e:
        print(f"Erro na IA: {e}")
        return {
            "descricao": f"Exercício {nome_exercicio} para fortalecimento e condicionamento físico.",
            "vantagens": "Melhora força, resistência, coordenação e saúde cardiovascular.",
            "passo_a_passo": "1. Posicione-se adequadamente. 2. Execute o movimento com controle. 3. Mantenha respiração constante."
        }

def async_route(f):
    """Decorator para rotas assíncronas"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# ROTAS DA API

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    """
    Cadastra um novo usuário no sistema
    
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: "João Silva"
            email:
              type: string
              example: "joao@email.com"
            idade:
              type: integer
              example: 25
            peso:
              type: number
              example: 70.5
            altura:
              type: number
              example: 1.75
            nivel_experiencia:
              type: string
              enum: [iniciante, intermediario, avancado]
              example: "iniciante"
    responses:
      201:
        description: Usuário cadastrado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
            usuario:
              type: object
      400:
        description: Dados inválidos
      409:
        description: Email já cadastrado
    """
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data or not all(k in data for k in ['nome', 'email', 'idade']):
            return jsonify({'error': 'Dados obrigatórios: nome, email, idade'}), 400
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar novo usuário
        usuario = Usuario(
            nome=data['nome'],
            email=data['email'],
            idade=data['idade'],
            peso=data.get('peso'),
            altura=data.get('altura'),
            nivel_experiencia=data.get('nivel_experiencia', 'iniciante')
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'usuario': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/buscar_usuario/<nome_usuario>', methods=['GET'])
def buscar_usuario(nome_usuario):
    """
    Busca um usuário específico pelo nome
    
    ---
    tags:
      - Usuários
    parameters:
      - name: nome_usuario
        in: path
        type: string
        required: true
        example: "João Silva"
    responses:
      200:
        description: Usuário encontrado
        schema:
          type: object
          properties:
            usuario:
              type: object
            estatisticas:
              type: object
              properties:
                total_exercicios:
                  type: integer
                exercicios_concluidos:
                  type: integer
                dias_cadastrado:
                  type: integer
      404:
        description: Usuário não encontrado
    """
    usuario = Usuario.query.filter_by(nome=nome_usuario).first()
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Atualizar último acesso
    usuario.ultimo_acesso = datetime.utcnow()
    db.session.commit()
    
    # Estatísticas do usuário
    exercicios = ExercicioPersonalizado.query.filter_by(usuario_id=usuario.id)
    total_exercicios = exercicios.count()
    exercicios_concluidos = exercicios.filter_by(concluido=True).count()
    dias_cadastrado = (datetime.utcnow() - usuario.data_cadastro).days
    
    return jsonify({
        'usuario': usuario.to_dict(),
        'estatisticas': {
            'total_exercicios': total_exercicios,
            'exercicios_concluidos': exercicios_concluidos,
            'dias_cadastrado': dias_cadastrado
        }
    }), 200

@app.route('/api/buscar_usuarios', methods=['GET'])
def buscar_usuarios():
    """
    Lista todos os usuários cadastrados
    
    ---
    tags:
      - Usuários
    parameters:
      - name: ativo
        in: query
        type: boolean
        required: false
        description: Filtrar apenas usuários ativos
      - name: nivel
        in: query
        type: string
        required: false
        description: Filtrar por nível de experiência
    responses:
      200:
        description: Lista de usuários
        schema:
          type: object
          properties:
            usuarios:
              type: array
              items:
                type: object
            total:
              type: integer
    """
    try:
        # Filtros opcionais
        query = Usuario.query
        
        if request.args.get('ativo') == 'true':
            query = query.filter_by(ativo=True)
        
        if request.args.get('nivel'):
            query = query.filter_by(nivel_experiencia=request.args.get('nivel'))
        
        usuarios = query.all()
        
        return jsonify({
            'usuarios': [usuario.to_dict() for usuario in usuarios],
            'total': len(usuarios)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deletar_usuario/<nome_usuario>', methods=['DELETE'])
def deletar_usuario(nome_usuario):
    """
    Deleta um usuário e seus exercícios
    
    ---
    tags:
      - Usuários
    parameters:
      - name: nome_usuario
        in: path
        type: string
        required: true
        example: "João Silva"
    responses:
      200:
        description: Usuário deletado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Usuário não encontrado
    """
    usuario = Usuario.query.filter_by(nome=nome_usuario).first()
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        # Deletar exercícios do usuário
        ExercicioPersonalizado.query.filter_by(usuario_id=usuario.id).delete()
        
        # Deletar usuário
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ROTAS EXTRAS CRIATIVAS

@app.route('/api/gerar_exercicio_personalizado/<nome_usuario>', methods=['POST'])
@async_route
async def gerar_exercicio_personalizado(nome_usuario):
    """
    Gera um exercício personalizado para o usuário usando IA
    
    ---
    tags:
      - Exercícios
    parameters:
      - name: nome_usuario
        in: path
        type: string
        required: true
        example: "João Silva"
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            nome_exercicio:
              type: string
              example: "Polichinelo"
    responses:
      200:
        description: Exercício gerado com sucesso
        schema:
          type: object
          properties:
            exercicio:
              type: object
            mensagem:
              type: string
      404:
        description: Usuário não encontrado
    """
    usuario = Usuario.query.filter_by(nome=nome_usuario).first()
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    data = request.get_json() or {}
    nome_exercicio = data.get('nome_exercicio', random.choice(EXERCICIOS_PERMITIDOS))
    
    # Gerar conteúdo com IA
    conteudo_ia = await gerar_exercicio_com_ia(nome_exercicio, usuario.nivel_experiencia)
    
    # Criar exercício personalizado
    exercicio = ExercicioPersonalizado(
        usuario_id=usuario.id,
        nome=nome_exercicio,
        descricao=conteudo_ia['descricao'],
        vantagens=conteudo_ia['vantagens'],
        passo_a_passo=conteudo_ia['passo_a_passo'],
        nivel_dificuldade=usuario.nivel_experiencia
    )
    
    db.session.add(exercicio)
    
    # Atualizar contador do usuário
    usuario.total_exercicios += 1
    usuario.ultimo_acesso = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'exercicio': exercicio.to_dict(),
        'mensagem': f'Exercício "{nome_exercicio}" gerado personalizado para {usuario.nome}'
    }), 200

@app.route('/api/exercicios_usuario/<nome_usuario>', methods=['GET'])
def exercicios_usuario(nome_usuario):
    """
    Lista exercícios de um usuário específico
    
    ---
    tags:
      - Exercícios
    parameters:
      - name: nome_usuario
        in: path
        type: string
        required: true
        example: "João Silva"
      - name: concluido
        in: query
        type: boolean
        required: false
        description: Filtrar por status de conclusão
    responses:
      200:
        description: Lista de exercícios
        schema:
          type: object
          properties:
            exercicios:
              type: array
              items:
                type: object
            total:
              type: integer
      404:
        description: Usuário não encontrado
    """
    usuario = Usuario.query.filter_by(nome=nome_usuario).first()
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    query = ExercicioPersonalizado.query.filter_by(usuario_id=usuario.id)
    
    if request.args.get('concluido') == 'true':
        query = query.filter_by(concluido=True)
    elif request.args.get('concluido') == 'false':
        query = query.filter_by(concluido=False)
    
    exercicios = query.order_by(ExercicioPersonalizado.data_criacao.desc()).all()
    
    return jsonify({
        'exercicios': [ex.to_dict() for ex in exercicios],
        'total': len(exercicios)
    }), 200

@app.route('/api/concluir_exercicio/<int:exercicio_id>', methods=['PATCH'])
def concluir_exercicio(exercicio_id):
    """
    Marca um exercício como concluído
    
    ---
    tags:
      - Exercícios
    parameters:
      - name: exercicio_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Exercício concluído com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
            exercicio:
              type: object
      404:
        description: Exercício não encontrado
    """
    exercicio = ExercicioPersonalizado.query.get(exercicio_id)
    if not exercicio:
        return jsonify({'error': 'Exercício não encontrado'}), 404
    
    exercicio.concluido = True
    exercicio.data_conclusao = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Exercício concluído com sucesso!',
        'exercicio': exercicio.to_dict()
    }), 200

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas_gerais():
    """
    Retorna estatísticas gerais do sistema
    
    ---
    tags:
      - Estatísticas
    responses:
      200:
        description: Estatísticas do sistema
        schema:
          type: object
          properties:
            total_usuarios:
              type: integer
            total_exercicios:
              type: integer
            exercicios_concluidos:
              type: integer
            usuarios_por_nivel:
              type: object
    """
    total_usuarios = Usuario.query.count()
    total_exercicios = ExercicioPersonalizado.query.count()
    exercicios_concluidos = ExercicioPersonalizado.query.filter_by(concluido=True).count()
    
    # Usuários por nível
    usuarios_por_nivel = {}
    for nivel in ['iniciante', 'intermediario', 'avancado']:
        usuarios_por_nivel[nivel] = Usuario.query.filter_by(nivel_experiencia=nivel).count()
    
    return jsonify({
        'total_usuarios': total_usuarios,
        'total_exercicios': total_exercicios,
        'exercicios_concluidos': exercicios_concluidos,
        'usuarios_por_nivel': usuarios_por_nivel
    }), 200

# Rota para servir o arquivo Swagger
@app.route('/static/swagger.json')
def swagger_json():
    """Retorna a documentação Swagger em JSON"""
    swagger_doc = {
        "openapi": "3.0.0",
        "info": {
            "title": "Fitness API - Sistema de Usuários e Exercícios",
            "description": "API para gerenciamento de usuários e geração de exercícios personalizados com IA",
            "version": "1.0.0",
            "contact": {
                "name": "PUC-RJ MVP",
                "email": "mvp@puc-rj.edu.br"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Servidor de desenvolvimento"
            }
        ],
        "tags": [
            {
                "name": "Usuários",
                "description": "Operações relacionadas aos usuários"
            },
            {
                "name": "Exercícios",
                "description": "Operações relacionadas aos exercícios personalizados"
            },
            {
                "name": "Estatísticas",
                "description": "Estatísticas gerais do sistema"
            }
        ],
        "paths": {
            "/api/cadastrar_usuario": {
                "post": {
                    "tags": ["Usuários"],
                    "summary": "Cadastra um novo usuário",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "nome": {"type": "string", "example": "João Silva"},
                                        "email": {"type": "string", "example": "joao@email.com"},
                                        "idade": {"type": "integer", "example": 25},
                                        "peso": {"type": "number", "example": 70.5},
                                        "altura": {"type": "number", "example": 1.75},
                                        "nivel_experiencia": {"type": "string", "enum": ["iniciante", "intermediario", "avancado"], "example": "iniciante"}
                                    },
                                    "required": ["nome", "email", "idade"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Usuário cadastrado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "usuario": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Dados inválidos"},
                        "409": {"description": "Email já cadastrado"}
                    }
                }
            },
            "/api/buscar_usuario/{nome_usuario}": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Busca um usuário específico pelo nome",
                    "parameters": [
                        {
                            "name": "nome_usuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "example": "João Silva"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Usuário encontrado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "usuario": {"type": "object"},
                                            "estatisticas": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuário não encontrado"}
                    }
                }
            },
            "/api/buscar_usuarios": {
                "get": {
                    "tags": ["Usuários"],
                    "summary": "Lista todos os usuários cadastrados",
                    "parameters": [
                        {
                            "name": "ativo",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Filtrar apenas usuários ativos"
                        },
                        {
                            "name": "nivel",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Filtrar por nível de experiência"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de usuários",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "usuarios": {"type": "array", "items": {"type": "object"}},
                                            "total": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/deletar_usuario/{nome_usuario}": {
                "delete": {
                    "tags": ["Usuários"],
                    "summary": "Deleta um usuário e seus exercícios",
                    "parameters": [
                        {
                            "name": "nome_usuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "example": "João Silva"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Usuário deletado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuário não encontrado"}
                    }
                }
            },
            "/api/gerar_exercicio_personalizado/{nome_usuario}": {
                "post": {
                    "tags": ["Exercícios"],
                    "summary": "Gera um exercício personalizado para o usuário usando IA",
                    "parameters": [
                        {
                            "name": "nome_usuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "example": "João Silva"
                        }
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "nome_exercicio": {"type": "string", "example": "Polichinelo"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Exercício gerado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "exercicio": {"type": "object"},
                                            "mensagem": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuário não encontrado"}
                    }
                }
            },
            "/api/exercicios_usuario/{nome_usuario}": {
                "get": {
                    "tags": ["Exercícios"],
                    "summary": "Lista exercícios de um usuário específico",
                    "parameters": [
                        {
                            "name": "nome_usuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "example": "João Silva"
                        },
                        {
                            "name": "concluido",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Filtrar por status de conclusão"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de exercícios",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "exercicios": {"type": "array", "items": {"type": "object"}},
                                            "total": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuário não encontrado"}
                    }
                }
            },
            "/api/concluir_exercicio/{exercicio_id}": {
                "patch": {
                    "tags": ["Exercícios"],
                    "summary": "Marca um exercício como concluído",
                    "parameters": [
                        {
                            "name": "exercicio_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "example": 1
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Exercício concluído com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "exercicio": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Exercício não encontrado"}
                    }
                }
            },
            "/api/estatisticas": {
                "get": {
                    "tags": ["Estatísticas"],
                    "summary": "Retorna estatísticas gerais do sistema",
                    "responses": {
                        "200": {
                            "description": "Estatísticas do sistema",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "total_usuarios": {"type": "integer"},
                                            "total_exercicios": {"type": "integer"},
                                            "exercicios_concluidos": {"type": "integer"},
                                            "usuarios_por_nivel": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return jsonify(swagger_doc)

# Inicializar banco de dados
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
