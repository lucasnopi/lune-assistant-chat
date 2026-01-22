import streamlit as st
from openai import OpenAI
import os
import time

# Configuração da página
st.set_page_config(
      page_title="Assistente LUNE",
      page_icon="🌙",
      layout="centered"
)

# Estilo customizado
st.markdown("""
<style>
    .stApp {
            max-width: 800px;
                    margin: 0 auto;
                        }
                            .stChatMessage {
                                    padding: 1rem;
                                        }
                                        </style>
                                        """, unsafe_allow_html=True)

st.title("🌙 Assistente LUNE")

# Verificar variáveis de ambiente
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

if not api_key or not assistant_id:
      st.error("⚠️ Configure as variáveis de ambiente: OPENAI_API_KEY e ASSISTANT_ID")
      st.stop()

# Inicializar cliente OpenAI
client = OpenAI(api_key=api_key)

# Inicializar estado da sessão
if "thread_id" not in st.session_state:
      thread = client.beta.threads.create()
      st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
      st.session_state.messages = []

# Mostrar histórico de mensagens
for message in st.session_state.messages:
      with st.chat_message(message["role"]):
                st.markdown(message["content"])

  # Input do usuário
  if prompt := st.chat_input("Digite sua mensagem..."):
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
                  st.markdown(prompt)

        # Enviar para o Assistant
        with st.chat_message("assistant"):
                  with st.spinner("Pensando..."):
                                # Adicionar mensagem à thread
                                client.beta.threads.messages.create(
                                                  thread_id=st.session_state.thread_id,
                                                  role="user",
                                                  content=prompt
                                )

                      # Executar o assistant
                                run = client.beta.threads.runs.create(
                                    thread_id=st.session_state.thread_id,
                                    assistant_id=assistant_id
                                )

                      # Aguardar conclusão
                                while run.status in ["queued", "in_progress"]:
                                                  time.sleep(0.5)
                                                  run = client.beta.threads.runs.retrieve(
                                                      thread_id=st.session_state.thread_id,
                                                      run_id=run.id
                                                  )

                                # Recuperar resposta
                                if run.status == "completed":
                                                  messages = client.beta.threads.messages.list(
                                                                        thread_id=st.session_state.thread_id
                                                  )
                                                  assistant_message = messages.data[0].content[0].text.value
                                                  st.markdown(assistant_message)
                                                  st.session_state.messages.append({
                                                      "role": "assistant",
                                                      "content": assistant_message
                                                  })
  else:
                st.error(f"Erro: {run.status}")

# Botão para limpar conversa
if st.button("🗑️ Nova conversa"):
      thread = client.beta.threads.create()
      st.session_state.thread_id = thread.id
      st.session_state.messages = []
      st.rerun()
