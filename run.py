import os
from app import create_app
from app.extensions import db
from app.models import ALL_MODELS

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

@app.shell_context_processor
def make_shell_context():
    ctx = {'db': db}
    for model in ALL_MODELS:
        ctx[model.__name__] = model
    return ctx

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
