from flask import Flask

from app.routs.phone_rout import phone_blueprint

app = Flask(__name__)

app.register_blueprint(phone_blueprint)

if __name__ == '__main__':
    app.run()