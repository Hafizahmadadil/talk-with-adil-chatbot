import openai
import gradio as gr
import requests
import os

# Load your Azure OpenAI and Translator API keys from environment variables
AZURE_OPENAI_ENDPOINT = "https://talk-with-adil-ai.openai.azure.com/"
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")  # Must be set in Azure portal or .env
AZURE_DEPLOYMENT_NAME = "gptchat"

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = "eastus"  # Replace with your region
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"

def translate_text(text, to_language):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-type": "application/json"
    }
    body = [{"text": text}]
    params = f"&to={to_language}"
    response = requests.post(TRANSLATOR_ENDPOINT + params, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()[0]["translations"][0]["text"]
    else:
        return f"Translation error: {response.text}"

def chat_with_azure_openai(prompt):
    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version=2024-03-01"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 800
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"OpenAI Error: {response.text}"

def multilingual_chat(user_input, language):
    # Translate input to English
    if language != "en":
        translated_input = translate_text(user_input, "en")
    else:
        translated_input = user_input

    # Chat with Azure OpenAI
    ai_response = chat_with_azure_openai(translated_input)

    # Translate response back
    if language != "en":
        final_response = translate_text(ai_response, language)
    else:
        final_response = ai_response

    return final_response

# UI using Gradio
iface = gr.Interface(
    fn=multilingual_chat,
    inputs=[
        gr.Textbox(label="Enter your message"),
        gr.Radio(["en", "ur", "roman-ur"], label="Select Language (English, Urdu, Roman Urdu)")
    ],
    outputs="text",
    title="Talk with Adil - Multilingual AI Chatbot"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    iface.launch(server_name="0.0.0.0", server_port=port)

