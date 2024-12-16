
from flask import Flask
from views.lessons import lessons_blueprint

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(lessons_blueprint, url_prefix='/lessons')

if __name__ == '__main__':
    app.run(debug=True)
