from flask import Flask
import threading
import schedule
import time
import os
from dotenv import load_dotenv

import bot

load_dotenv()

app = Flask(__name__)

def run_scheduler():
    """Roda o job inicial e depois o schedule indefinidamente"""
    bot.logging.info("Iniciando a thread do scheduler do bot...")
    bot.job()
    schedule.every(5).hours.do(bot.job)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Inicia a thread de background apenas uma vez
@app.before_request
def activate_job():
    if not hasattr(app, "scheduler_started"):
        app.scheduler_started = True
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()

# Rota simples para o Render saber que o app está de pé (health check)
@app.route("/")
def home():
    return "UFAL Editais Bot está rodando!"

if __name__ == "__main__":
    # Quando rodar localmente com `python3 app.py`
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
