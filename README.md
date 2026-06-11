# Ufal Editais Bot

Este é um bot que verifica o site de editais da UFAL (https://editais.ufal.br/) a cada 5 horas e envia um e-mail com os editais novos ou atualizados.

## Requisitos

- Python 3.8+
- Bibliotecas do Python (veja `requirements.txt`)

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

O bot precisa de credenciais de e-mail para enviar as notificações. O projeto usa a biblioteca `python-dotenv` para carregar essas configurações a partir de um arquivo `.env`.

Para configurar, crie um arquivo chamado `.env` na mesma pasta do script (você pode copiar o `.env.example` se quiser) com o seguinte conteúdo:

```ini
EMAIL_USER=seu.email@gmail.com
EMAIL_PASS=sua_senha_ou_app_password
EMAILS_JSON_URL=https://raw.githubusercontent.com/usuario/repo/main/emails.json
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

O `EMAILS_JSON_URL` deve ser o link direto ("raw") para um arquivo `.json` (por exemplo, hospedado no GitHub) que contenha uma lista de e-mails em formato array, como este:
```json
[
  "email1@exemplo.com",
  "email2@exemplo.com"
]
```

> **Dica**: Se você usa o Gmail e tem a verificação em duas etapas ativada, crie uma "App Password" (Senha de Aplicativo) nas configurações do Google em vez de usar sua senha principal.

## Execução Local

Para rodar o bot normalmente a cada 5 horas:
```bash
python3 bot.py
```

Para testar o script e executar apenas uma vez na hora:
```bash
python3 bot.py --test
```

Para rodar como um servidor web (necessário para deploys em nuvem, usando Flask):
```bash
python3 app.py
# Ou com gunicorn: gunicorn app:app
```

## Deploy no Render

Este projeto já está configurado para ser facilmente hospedado como um **Web Service** gratuito no [Render](https://render.com/).

1. Crie uma nova conta/projeto no Render e escolha **Web Service**.
2. Conecte com o seu repositório do GitHub.
3. Nas configurações do Render, use:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Vá na aba **Environment** no Render e adicione todas as variáveis de ambiente necessárias (`EMAIL_USER`, `EMAIL_PASS`, `EMAILS_JSON_URL`).

O Render vai criar uma URL pública para o bot (como `seu-bot.onrender.com`). Acessar essa URL vai acender o servidor web e a thread de verificação em segundo plano começará a rodar a cada 5 horas. Você também pode usar serviços como o UptimeRobot para pingar a página e impedir que o servidor durma.

> **⚠️ Atenção sobre o arquivo de Estado no Render**: Web Services gratuitos no Render têm o sistema de arquivos "efêmero". Isso significa que se o servidor for reiniciado ou dormir por inatividade, o arquivo `state.json` será apagado e o bot vai "esquecer" os editais que já leu. Se isso for um problema, futuramente o arquivo de estado precisará ser migrado para um banco de dados simples (ex: PostgreSQL do próprio Render ou Supabase) ou para um Render Disk (pago).
