import gradio as gr
import requests
import os

API_URL = "http://localhost:8000"

def list_examples():
    response = requests.get(f"{API_URL}/examples/")
    return response.json()

def upload_example(audio, description, language):
    files = {"file": ("audio.wav", audio)}
    data = {"description": description, "language": language}
    response = requests.post(f"{API_URL}/examples/", files=files, data=data)
    return "Example uploaded successfully!"

def generate_audio(text, example_id, language):
    data = {
        "text": text,
        "example_id": example_id,
        "language": language
    }
    response = requests.post(f"{API_URL}/generate/", json=data)
    return response.json()["audio_path"]

def create_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Zonos Audio Example Manager")
        
        with gr.Tab("Upload Example"):
            audio_input = gr.Audio(type="filepath")
            description_input = gr.Textbox(label="Description")
            language_input = gr.Dropdown(choices=["en-us", "es-es", "fr-fr"], label="Language")
            upload_btn = gr.Button("Upload")
            upload_output = gr.Textbox(label="Result")
            
            upload_btn.click(
                upload_example,
                inputs=[audio_input, description_input, language_input],
                outputs=upload_output
            )
        
        with gr.Tab("Generate Audio"):
            text_input = gr.Textbox(label="Text to generate")
            example_id_input = gr.Number(label="Example ID")
            gen_language_input = gr.Dropdown(choices=["en-us", "es-es", "fr-fr"], label="Language")
            generate_btn = gr.Button("Generate")
            audio_output = gr.Audio(label="Generated Audio")
            
            generate_btn.click(
                generate_audio,
                inputs=[text_input, example_id_input, gen_language_input],
                outputs=audio_output
            )
        
        with gr.Tab("View Examples"):
            refresh_btn = gr.Button("Refresh Examples")
            examples_output = gr.JSON()
            
            refresh_btn.click(
                list_examples,
                outputs=examples_output
            )
    
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860) 