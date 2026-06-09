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

O bot precisa de credenciais de e-mail para enviar as notificações. Configure as seguintes variáveis de ambiente:

- `EMAIL_USER`: Seu endereço de e-mail (ex: `seu.email@gmail.com`)
- `EMAIL_PASS`: Sua senha ou "App Password" (se usar Gmail)
- `EMAIL_TO`: O endereço de e-mail que receberá os alertas
- `SMTP_SERVER`: O servidor SMTP (padrão: `smtp.gmail.com`)
- `SMTP_PORT`: A porta do SMTP (padrão: `587`)

No Linux/macOS:
```bash
export EMAIL_USER="seu.email@gmail.com"
export EMAIL_PASS="sua_senha"
export EMAIL_TO="destino@email.com"
```

## Execução

Para rodar o bot normalmente a cada 5 horas:
```bash
python3 bot.py
```

Para testar o script e executar apenas uma vez na hora:
```bash
python3 bot.py --test
```
