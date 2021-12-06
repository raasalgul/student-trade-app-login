from flask import Flask

application = Flask(__name__)

from userLogin import signIn,signUp