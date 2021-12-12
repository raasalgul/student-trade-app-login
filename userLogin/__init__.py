from flask import Flask

from flask_cors import CORS

application = Flask(__name__)
CORS(application)

from userLogin import signIn,signUp