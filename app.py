import datetime
import streamlit as st
import sqlite3

# Definir uma classe para representar um participante
class Participante:
    def __init__(self, nome, idade, sexo, profissao, escolaridade, telefone):
        self.nome = nome
        self.idade = idade
        self.sexo = sexo
        self.profissao = profissao
        self.escolaridade = escolaridade
        self.telefone = telefone
        self.frequencia = []

    def adicionar_frequencia(self, data):
        self.frequencia.append(data)

# Inicializar o st.session_state
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'participante_selecionado' not in st.session_state:
    st.session_state.participante_selecionado = None

# Função para cadastrar um participante via teclado
def cadastrar_participante_manualmente():
    with st.form("form_cadastro"):
        nome = st.text_input("Nome:")
        idade = st.number_input("Idade:", min_value=18)
        sexo = st.selectbox("Sexo:", ["Masculino", "Feminino", "Outro"])
        profissao = st.text_input("Profissão:")
        escolaridade = st.selectbox("Escolaridade:", ["Ensino Fundamental", "Ensino Médio", "Superior", "Pós-graduação"])
        telefone = st.text_input("Telefone:")
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            novo_participante = Participante(nome, idade, sexo, profissao, escolaridade, telefone)
            st.session_state.participantes.append(novo_participante)
            adicionar_participante_ao_banco(novo_participante)
            st.success("Participante cadastrado com sucesso!")
            gerar_relatorio()  # Atualiza o relatório após cada cadastro

# Função para gerar relatório
def gerar_relatorio():
    st.header("Relatório de Participantes")
    if st.session_state.participantes:
        for i, participante in enumerate(st.session_state.participantes):
            st.write(f"Nome: {participante.nome}")
            st.write(f"Idade: {participante.idade}")
            st.write(f"Sexo: {participante.sexo}")
            st.write(f"Profissão: {participante.profissao}")
            st.write(f"Escolaridade: {participante.escolaridade}")
            st.write(f"Telefone: {participante.telefone}")
            st.write(f"Frequência: {', '.join(participante.frequencia)}")
            
            # Botão para selecionar o participante fora do formulário
            if st.button(f"Selecionar {participante.nome} para registrar presença", key=f"select_{i}"):
                st.session_state.participante_selecionado = i

# Criar uma conexão com o banco de dados
conn = sqlite3.connect('participantes.db')
cursor = conn.cursor()

# Criar a tabela (se não existir)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        idade INTEGER,
        sexo TEXT,
        profissao TEXT,
        escolaridade TEXT,
        telefone TEXT,
        frequencia INTEGER
    )
''')

# Criar a tabela de presença (se não existir)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS presenca (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participante_id INTEGER,
        data DATE
    )
''')

# Função para adicionar um participante ao banco de dados
def adicionar_participante_ao_banco(participante):
    cursor.execute('''
        INSERT INTO participantes (nome, idade, sexo, profissao, escolaridade, telefone, frequencia)
        VALUES (?, ?, ?, ?, ?, ?, ?)
     ''', (participante.nome, participante.idade, participante.sexo, participante.profissao, participante.escolaridade, participante.telefone, len(participante.frequencia)))
    conn.commit()

# Função para registrar presença
def registrar_presenca():
    if st.session_state.participante_selecionado is None:
        st.warning("Nenhum participante selecionado.")
        return

    participante = st.session_state.participantes[st.session_state.participante_selecionado]
    data = datetime.date.today()

    # Inserir a presença
    cursor.execute('''
        INSERT INTO presenca (participante_id, data)
        VALUES (?, ?)
    ''', (st.session_state.participante_selecionado, data))
    conn.commit()

    participante.adicionar_frequencia(str(data))
    atualizar_frequencia(st.session_state.participante_selecionado)
    st.success(f"Presença registrada para {participante.nome}.")

# Função para atualizar a frequência do participante no banco
def atualizar_frequencia(participante_id):
    cursor.execute('''
        SELECT COUNT(*) FROM presenca
        WHERE participante_id = ?
    ''', (participante_id,))
    frequencia = cursor.fetchone()[0]

    cursor.execute('''
        UPDATE participantes
        SET frequencia = ?
        WHERE id = ?
    ''', (frequencia, participante_id))
    conn.commit()

# Gerar o relatório de participantes ao iniciar
gerar_relatorio()

# Botão para marcar presença fora do formulário
if st.button("Marcar Presença"):
    registrar_presenca()

# Footer
st.markdown('''
<div style="text-align: center; padding: 20px;">
    Pastores responsáveis: Marcos e Clodoaldo | Grupo de Varões | ADFidelidade
    <br>
    Criado por: @Fthec
    <br>
    &copy; 2024 Todos os direitos reservados
</div>
''', unsafe_allow_html=True)

# Chamar a função cadastrar_participante_manualmente()
cadastrar_participante_manualmente()

# Fechar a conexão ao finalizar
conn.close()
