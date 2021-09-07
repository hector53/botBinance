from flask import Flask
from datos import *
app = Flask(__name__)
app.secret_key = datos["secret_key_login"]

#aqui se viene todo 
from app.request import *