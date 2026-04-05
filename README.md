# 🎙️ Transcritor de Vídeos Web (Whisper + Gradio)

Uma aplicação web leve e local para transcrever áudios e vídeos utilizando a inteligência artificial **Whisper** (da OpenAI). Com uma interface amigável construída em **Gradio**, você pode rodar este servidor no seu computador e acessá-lo pelo celular (ou qualquer outro dispositivo na mesma rede Wi-Fi) para fazer uploads e obter as transcrições em texto.

---

## ✨ Funcionalidades

- **Processamento 100% Local:** Suas mídias não são enviadas para a nuvem. A transcrição acontece no seu próprio hardware.
- **Acesso Remoto Local:** Acesse a interface web via navegador pelo celular usando o IP da máquina host.
- **Extração Automática:** Não é necessário extrair o áudio do vídeo manualmente; o sistema aceita `.mp4`, `.mkv`, `.avi`, etc., e faz a conversão em segundo plano.

---

## 🛠️ Pré-requisitos

Antes de começar, você precisa ter instalado no seu sistema:

1. **Python 3.8 ou superior** (Recomendado: 3.10+)
2. **FFmpeg:** Um software essencial de processamento de mídia que o Whisper utiliza nos bastidores.

### Como instalar o FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows** — Abra o terminal como administrador e rode:
```bash
winget install ffmpeg
```
> Feche e reabra o terminal após a instalação.

**macOS:**
```bash
brew install ffmpeg
```

---

## 🚀 Instalação Passo a Passo

### 1. Clone o repositório ou baixe os arquivos

Abra o terminal e entre na pasta onde deseja colocar o projeto:

```bash
git clone https://github.com/gabedsam01/transcricao.git
cd transcricao
```

> Se não estiver usando Git, basta criar a pasta manualmente e colocar os arquivos `app_web.py` e `requirements.txt` dentro dela.

---

### 2. Crie um Ambiente Virtual (Venv)

Isso garante que as dependências do projeto não entrem em conflito com o seu sistema.

**Linux/macOS:**
```bash
python3 -m venv venv
```

**Windows:**
```bash
python -m venv venv
```

---

### 3. Ative o Ambiente Virtual

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (Prompt de Comando):**
```bash
venv\Scripts\activate
```

---

### 4. Instale as Dependências

Com o ambiente ativado (você verá `(venv)` no início da linha de comando), instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

---

## 💻 Como Executar

Sempre que quiser rodar a aplicação, certifique-se de que o ambiente virtual está ativado e execute:

```bash
python app_web.py
```

- **No próprio computador:** Abra o navegador e acesse `http://localhost:5000` ou `http://127.0.0.1:5000`.
- **Pelo celular (mesmo Wi-Fi):**
  1. Descubra o IP local do seu computador:
     - Linux: `hostname -I`
     - Windows: `ipconfig`
  2. No navegador do celular, acesse: `http://<SEU_IP_LOCAL>:5000`
     - Exemplo: `http://192.168.1.15:5000`

> **Nota:** Na primeira execução, o script fará o download do modelo de IA. Isso pode levar alguns minutos dependendo da sua internet. Nas próximas vezes, o carregamento será instantâneo.

---

## ⚙️ Dicas Avançadas

### Rodando em Segundo Plano (via SSH)

Se você iniciou o servidor via SSH e não quer que ele feche ao desconectar, utilize o `nohup` (Linux/macOS):

```bash
nohup python app_web.py > log.txt 2>&1 &
```

Isso manterá o servidor rodando em background. Para encerrá-lo depois:

```bash
ps aux | grep app_web.py
kill <PID>
```

---

### Trocando o Tamanho do Modelo

Por padrão, o script utiliza o modelo `base`, que oferece um ótimo equilíbrio entre velocidade e precisão. Para transcrições mais precisas (ao custo de maior tempo de processamento), edite o arquivo `app_web.py` e altere a linha:

```python
modelo = whisper.load_model("base")
# Opções: "tiny", "base", "small", "medium", "large"
```

| Modelo   | Velocidade | Precisão  |
|----------|------------|-----------|
| `tiny`   | ⚡⚡⚡⚡⚡ | ⭐        |
| `base`   | ⚡⚡⚡⚡   | ⭐⭐      |
| `small`  | ⚡⚡⚡     | ⭐⭐⭐    |
| `medium` | ⚡⚡       | ⭐⭐⚡⭐  |
| `large`  | ⚡         | ⭐⭐⭐⭐⭐ |

---

Desenvolvido com Python, [OpenAI Whisper](https://github.com/openai/whisper) e [Gradio](https://www.gradio.app/).
# transcricao
