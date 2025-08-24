import os
from flask import send_from_directory
from app import create_app

app = create_app()

# Serve frontend build
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists("frontend/dist/" + path):
        return send_from_directory("frontend/dist", path)
    else:
        return send_from_directory("frontend/dist", "index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
