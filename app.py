


#from tenderix
import os
import diskcache
import logging
from dash import Dash
from dash import DiskcacheManager
from flask import Flask
from flask_session import Session
from dotenv import load_dotenv
from locales import load_locale
from index import layout, register_callbacks
from models import db

#from chatGPT
# Register Blueprints
#app.register_blueprint(lessons_blueprint, url_prefix='/lessons')

#from tenderix
load_dotenv()
page_name = "app"
text_data = load_locale(page_name)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger(__name__)

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

# Flask server setup
server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ["SERVER_SECRET_KEY"]
server.config['SESSION_TYPE'] = 'filesystem'

# Database configuration
DATABASE_URL = os.environ['DB_URL']
server.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

external_stylesheets = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
]

external_scripts = [
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js'
]

# Initialize database
db.init_app(server)
with server.app_context():
    db.create_all()

Session(server)

# Dash app setup
app = Dash(__name__,
           server=server,
           external_stylesheets=external_stylesheets,
           external_scripts=external_scripts,
           suppress_callback_exceptions=True,
           update_title=None,
           meta_tags=[
               {'name': 'description', 'content': text_data["description"]},
               {'name': 'keywords', 'content': text_data["keywords"]},
               {'name': 'author', 'content': text_data["author"]},
               ]
          )

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        <script type="text/javascript">
            (function(c,l,a,r,i,t,y){{
                c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
                t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            }})(window, document, "clarity", "script", "{ClarityInsightID}");
        </script>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
""".format(ClarityInsightID=os.environ["ClarityInsightID"])

app.title = text_data["title"]
app.layout = layout
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)