from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig
from time import sleep
from flask import Flask, request

app = Flask(__name__)

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

LOGGER = getLogger(__name__)

@app.route('/')
def homepage():
    return "<h1>TeleBullet By MasterMind!</h1>"

@app.errorhandler(Exception)
def page_not_found(e):
    return f"<h1>404: WebPage not found! </h1><h2>Error: {e}</h2>", 404

if __name__ == "__main__":
    app.run()

