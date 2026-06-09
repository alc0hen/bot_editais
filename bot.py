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

def send_email(new_editais):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    email_to = os.environ.get('EMAIL_TO')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))

    if not email_user or not email_pass or not email_to:
        logging.warning("Variáveis de ambiente de e-mail não configuradas (EMAIL_USER, EMAIL_PASS, EMAIL_TO). Pulando o envio de e-mail.")
        return False

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_to
    msg['Subject'] = 'Novos Editais da UFAL Encontrados!'

    body = "Os seguintes editais foram publicados ou atualizados:\n\n"
    for ed in new_editais:
        status_text = f" [{ed['status']}]" if ed['status'] else ""
        body += f"- {ed['title']}{status_text}\n  Link: {ed['link']}\n\n"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, email_to, text)
        server.quit()
        logging.info("E-mail enviado com sucesso!")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
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

        email_configured = bool(os.environ.get('EMAIL_USER') and os.environ.get('EMAIL_PASS') and os.environ.get('EMAIL_TO'))
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
