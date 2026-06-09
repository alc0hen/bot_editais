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
EMAIL_TO=destino@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

> **Dica**: Se você usa o Gmail e tem a verificação em duas etapas ativada, crie uma "App Password" (Senha de Aplicativo) nas configurações do Google em vez de usar sua senha principal.

## Execução

Para rodar o bot normalmente a cada 5 horas:
```bash
python3 bot.py
```

Para testar o script e executar apenas uma vez na hora:
```bash
python3 bot.py --test
```
