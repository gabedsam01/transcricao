import gradio as gr
import whisper

# 1. Carrega o modelo de IA
print("Carregando o modelo Whisper... Aguarde.")
modelo = whisper.load_model("base")
print("Modelo carregado com sucesso!")

# 2. Função que faz a transcrição
def transcrever_video(caminho_video):
    if caminho_video is None:
        return "Nenhum arquivo recebido."
    
    print("Transcrevendo arquivo recebido...")
    resultado = modelo.transcribe(caminho_video)
    return resultado["text"]

# 3. Criando a Interface Web (sem os parâmetros obsoletos)
interface = gr.Interface(
    fn=transcrever_video,
    inputs=gr.Video(label="Faça o upload do seu vídeo aqui"),
    outputs=gr.Textbox(label="Texto Transcrito", lines=15),
    title="Transcritor Web - Whisper",
    description="Acesse do celular, envie um vídeo e aguarde a transcrição."
)

# 4. Iniciando o servidor web
if __name__ == "__main__":
    # server_name="0.0.0.0" permite acesso pela rede local
    # server_port=5000 é a porta de acesso
    interface.launch(server_name="0.0.0.0", server_port=5000)
