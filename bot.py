import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import argparse
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = 'https://editais.ufal.br/'
STATE_FILE = 'state.json'

def fetch_editais():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao acessar {URL}: {e}")
        return []

    soup = BeautifulSoup(r.content, 'html.parser')
    editais = []

    content = soup.find('article', id='content')
    if content:
        dados_divs = content.find_all('div', class_='dados')
        for div in dados_divs:
            a_tag = div.find('a', class_='titulo')
            if not a_tag:
                continue

            title = a_tag.text.strip()
            link = a_tag.get('href')

            data_div = div.find('div', class_='data')
            status = ""
            if data_div:
                status_span = data_div.find('span', class_='atualizado')
                if status_span:
                    status = status_span.text.strip()

            editais.append({
                'title': title,
                'link': link,
                'status': status
            })
    return editais

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar state.json: {e}")
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Erro ao salvar state.json: {e}")

def fetch_email_list():
    url = os.environ.get('EMAILS_JSON_URL')
    if not url:
        logging.warning("Variável EMAILS_JSON_URL não configurada.")
        return []

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        emails = r.json()
        if isinstance(emails, list):
            return emails
        else:
            logging.error("O arquivo JSON de e-mails deve ser uma lista (array).")
            return []
    except Exception as e:
        logging.error(f"Erro ao buscar lista de e-mails de {url}: {e}")
        return []

def send_email(new_editais):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    emails_json_url = os.environ.get('EMAILS_JSON_URL')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))

    if not email_user or not email_pass or not emails_json_url:
        logging.warning("Variáveis de ambiente de e-mail não configuradas (EMAIL_USER, EMAIL_PASS, EMAILS_JSON_URL). Pulando o envio de e-mail.")
        return False

    email_list = fetch_email_list()
    if not email_list:
        logging.warning("Lista de e-mails vazia ou falha ao buscar. Pulando envio.")
        return False

    body = "Os seguintes editais foram publicados ou atualizados:\n\n"
    for ed in new_editais:
        status_text = f" [{ed['status']}]" if ed['status'] else ""
        body += f"- {ed['title']}{status_text}\n  Link: {ed['link']}\n\n"

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_pass)

        for email_to in email_list:
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_to
            msg['Subject'] = 'Novos Editais da UFAL Encontrados!'
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            try:
                server.sendmail(email_user, email_to, msg.as_string())
                logging.info(f"E-mail enviado com sucesso para {email_to}")
            except Exception as e:
                logging.error(f"Erro ao enviar e-mail para {email_to}: {e}")

        server.quit()
        return True
    except Exception as e:
        logging.error(f"Erro ao conectar ao servidor SMTP: {e}")
        return False

def job():
    logging.info("Verificando editais...")
    editais = fetch_editais()
    if not editais:
        logging.info("Nenhum edital encontrado no site.")
        return

    state = load_state()
    new_editais = []

    for ed in editais:
        link = ed['link']
        status = ed['status']

        # If the edital is completely new, or if its status changed (e.g. to "Atualizado")
        if link not in state:
            new_editais.append(ed)
            state[link] = status
        elif state[link] != status:
            # Maybe it became "Atualizado"
            new_editais.append(ed)
            state[link] = status

    if new_editais:
        logging.info(f"Encontrados {len(new_editais)} editais novos ou atualizados.")
        # Send email
        email_sent = send_email(new_editais)

        email_configured = bool(os.environ.get('EMAIL_USER') and os.environ.get('EMAIL_PASS') and os.environ.get('EMAILS_JSON_URL'))
        if email_sent or not email_configured:
            save_state(state)
    else:
        logging.info("Nenhum edital novo ou atualizado.")

def main():
    parser = argparse.ArgumentParser(description='Bot de Editais da UFAL')
    parser.add_argument('--test', action='store_true', help='Roda o bot uma vez e sai')
    args = parser.parse_args()

    if args.test:
        logging.info("Rodando em modo de teste (uma execução).")
        job()
    else:
        logging.info("Iniciando o bot (rodando a cada 5 horas).")
        job()  # Run once at startup
        schedule.every(5).hours.do(job)

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
