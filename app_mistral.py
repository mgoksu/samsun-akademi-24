
import streamlit as st
from htmlTemplates import css, bot_template, user_template
from mistralai import Mistral
from dotenv import load_dotenv
import os

from util import read_pdf_content

load_dotenv()


PROMPT_TEMPLATE = (
    "Bağlam:{context}\n\nSoru:{instruction}\n"
)
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
AGENT_ID=os.getenv("AGENT_ID")
CLIENT=Mistral(api_key=MISTRAL_API_KEY)
# Verilen metinden 10 tane çoktan seçmeli soru hazırla.

def prepare_prompt(query):
    context = st.texts
    prompt = PROMPT_TEMPLATE.format_map({'instruction': query, 'context': context})
    return prompt

def bot_template_generator_wrapper(generator):
    result = ""
    container = st.empty()
    for content in generator:
        result += content
        container.write(bot_template.replace("{{MSG}}", result),unsafe_allow_html=True)
    return result

def handle_question(question):
    # rewrite chat history so that older messages don't get lost
    for i,msg in enumerate(st.session_state.chat_history):
        if i%2==0:
            st.write(user_template.replace("{{MSG}}",msg,),unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}",msg),unsafe_allow_html=True)
    
    prompt = prepare_prompt(question)
    print(prompt)
    st.session_state.chat_history.append(question)
    st.write(user_template.replace("{{MSG}}",question),unsafe_allow_html=True)

    chat_response = CLIENT.agents.complete(
        agent_id=AGENT_ID,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    response = chat_response.choices[0].message.content
    print(response)
    st.session_state.chat_history.append(response)
    st.write(bot_template.replace("{{MSG}}",response),unsafe_allow_html=True)

def main():
    st.write(css,unsafe_allow_html=True)

    if "texts" not in st.session_state:
        st.session_state.texts = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]
    
    st.header("Türkçe PDF dosyalarıyla sohbet")
    question=st.text_input("Soru sor:")
    if question:
        handle_question(question)
    with st.sidebar:
        st.subheader("Dökümanlar")
        docs=st.file_uploader("PDF dosyalarını yükleyip 'Dökümanları işle' butonuna tıklayın",accept_multiple_files=True)
        if st.button("Dökümanları işle"):
            with st.spinner("İşleniyor..."):
                
                # load the pdf
                raw_text = read_pdf_content(docs)
                
                st.texts = raw_text


if __name__ == '__main__':
    main()