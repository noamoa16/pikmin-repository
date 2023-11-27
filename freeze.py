from flask_frozen import Freezer
from server import app
from pathlib import Path

freezer = Freezer(app)
app.config['FREEZER_DESTINATION'] = str(Path(__file__).parent / 'docs')
app.config['FREEZER_RELATIVE_URLS'] = True

if __name__ == '__main__':
    freezer.freeze()