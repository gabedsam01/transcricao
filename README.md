# 🎙️ Transcription API (Whisper)

API REST robusta e leve para transcrição de áudio e vídeo utilizando o modelo **Whisper** da OpenAI. Otimizada para execução em ambientes com recursos limitados (como VPS Oracle ARM64) utilizando **FastAPI** e **Docker**.

## ✨ Funcionalidades

- **API REST Stateless:** Fácil de integrar com qualquer frontend (Lovable, React, Vue, etc).
- **Processamento em Segundo Plano:** Utiliza FFmpeg para processar diversos formatos de mídia (.mp4, .mp3, .wav, .mkv, etc).
- **Otimização de Memória:** Streaming de upload em chunks para evitar estouro de RAM em arquivos grandes.
- **Warm-up de Modelo:** O modelo é carregado na inicialização para garantir respostas rápidas no primeiro request.

## 🚀 Deploy e CI/CD

### GitHub Actions (CI/CD Multi-Arch)
O projeto inclui um workflow automatizado que constrói e publica a imagem Docker para `linux/amd64` (x86_64) e `linux/arm64` no Docker Hub sempre que há um push na branch `main`.

#### 🔑 Configuração de Secrets no GitHub
Para que o workflow funcione, você deve adicionar os seguintes secrets no seu repositório (**Settings > Secrets and variables > Actions**):

1. `DOCKERHUB_USERNAME`: Seu nome de usuário no Docker Hub (ex: `gabedsam01`).
2. `DOCKERHUB_TOKEN`: Um Personal Access Token gerado no Docker Hub (**Account Settings > Security > Personal access tokens**).

#### ✅ Como Verificar a Imagem Multi-Arch
Após o término do workflow, você pode verificar se a imagem suporta ambas as arquiteturas usando o comando:

```bash
docker manifest inspect gabedsam01/whisper-local-api:latest
```

No campo `platforms`, você deverá ver entradas para `amd64` e `arm64`.

## ⚙️ Variáveis de Ambiente

Configure estas variáveis no seu arquivo `.env` ou diretamente no ambiente do Docker:

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `WHISPER_MODEL` | Tamanho do modelo (`tiny`, `base`, `small`, `medium`, `large`) | `medium` |
| `WHISPER_LANGUAGE` | Forçar um idioma específico (ex: `pt`, `en`) | Auto-detect |
| `MAX_FILE_SIZE_MB` | Limite máximo de upload em Megabytes | `500` |
| `PORT` | Porta onde a API será exposta | `8000` |

## 🚀 Deploy no Portainer / Docker Compose

Para rodar a API no seu servidor, basta copiar o conteúdo abaixo e colar no seu **Stack** do Portainer ou criar um arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  whisper-api:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - WHISPER_MODEL=${WHISPER_MODEL:-medium}
      - WHISPER_LANGUAGE=${WHISPER_LANGUAGE}
      - MAX_FILE_SIZE_MB=${MAX_FILE_SIZE_MB:-500}
    volumes:
      - whisper-cache:/root/.cache/whisper
    deploy:
      resources:
        limits:
          memory: 12G

volumes:
  whisper-cache:
```

## 🔌 Guia de Conexão (Lovable / Frontend)

Exemplo de como conectar seu frontend Lovable à API de transcrição:

```javascript
const transcribeAudio = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('https://sua-api.com/transcribe', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Falha na transcrição');
    
    const data = await response.json();
    console.log('Texto transcrito:', data.text);
    return data;
  } catch (error) {
    console.error('Erro:', error);
  }
};
```

## 📍 Endpoints

### `GET /health`
Verifica se a API está online e qual modelo está carregado.

**Resposta de Exemplo:**
```json
{
  "status": "ok",
  "model": "medium",
  "device": "cpu"
}
```

### `POST /transcribe`
Faz o upload de um arquivo e retorna a transcrição completa.

**Parâmetros (Form Data):**
- `file`: Arquivo de áudio ou vídeo.

**Resposta de Exemplo:**
```json
{
  "text": "Conteúdo da transcrição...",
  "language": "pt",
  "segments": [...],
  "usage_example": "fetch('URL/transcribe', { method: 'POST', body: new FormData().append('file', file) })"
}
```

---
Desenvolvido com FastAPI e OpenAI Whisper.
