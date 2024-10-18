
from threading import Thread

import streamlit as st
from htmlTemplates import css, bot_template, user_template
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
import torch

# Sampling parameters
# Deterministic generation
SAMPLING_PARAMS = {
    'do_sample': False,
    'top_k': 50,
    'top_p': None,
    'temperature': None,
    'repetition_penalty': 1.0,
    'max_new_tokens': 1024,
}

# LLM parameters
LLM_MODEL_NAME = "sambanovasystems/SambaLingo-Turkish-Chat"
PROMPT_TEMPLATE = (
    "<|user|>Soru:{query}</s>\n"
    "<|assistant|>\n"
)
# Siber zorbalık üzerine bir sunum hazırla. Her bir slayt için içeriği açıkça yaz.


# Streamlit seems to load the resources multiple times
# So it needs to be cached to avoid running out of memory
# https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
@st.cache_resource
def load_tokenizer():
    return AutoTokenizer.from_pretrained(LLM_MODEL_NAME)

@st.cache_resource
def load_model():
    if torch.cuda.is_available():
        return AutoModelForCausalLM.from_pretrained(LLM_MODEL_NAME, 
                                                    device_map='auto', 
                                                    quantization_config=BNB_CONFIG,
                                                    )
    else:
        return AutoModelForCausalLM.from_pretrained(LLM_MODEL_NAME)

@st.cache_resource
def load_streamer():
    return TextIteratorStreamer(TOKENIZER, skip_prompt=True, skip_special_tokens=True)

@st.cache_resource
def load_bnb_config():
    return BitsAndBytesConfig(
        load_in_8bit=True,
    )

BNB_CONFIG = load_bnb_config()

TOKENIZER = load_tokenizer()
MODEL = load_model()
STREAMER = load_streamer()

def prepare_prompt(query):
    prompt = PROMPT_TEMPLATE.format_map({'query': query})

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
    st.session_state.chat_history.append(question)
    st.write(user_template.replace("{{MSG}}",question),unsafe_allow_html=True)
    inputs = TOKENIZER(prompt, return_tensors="pt")
    inputs['input_ids'] = inputs['input_ids'].to(MODEL.device)

    thread = Thread(target=MODEL.generate, kwargs=dict(inputs, 
                                                       **SAMPLING_PARAMS,
                                                       streamer=STREAMER,
                                                       pad_token_id=TOKENIZER.eos_token_id, 
                                                       ),
                                                       )
    thread.start()
    response = bot_template_generator_wrapper(STREAMER)
    st.session_state.chat_history.append(response)

def main():
    st.write(css,unsafe_allow_html=True)

    if "index" not in st.session_state:
        st.session_state.index = None

    if "split_texts" not in st.session_state:
        st.session_state.split_texts = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]
    
    st.header("Türkçe sohbet")
    question=st.text_input("Soru sor:")
    if question:
        handle_question(question)

if __name__ == '__main__':
    main()