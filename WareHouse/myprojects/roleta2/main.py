'''
Flask application that serves the wheel-of-names web app.
Run: pip install flask
Then: python main.py
Access: http://127.0.0.1:5000/
'''
from flask import Flask, render_template
import os
def create_app():
    """
    Create and configure the Flask application.
    Serves templates from 'templates' and static files from 'static'.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    @app.route('/')
    def index():
        """
        Serve the main page.
        """
        return render_template('index.html')
    return app
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    # debug=True for development; set to False in production
    app.run(debug=True, host='0.0.0.0', port=port)