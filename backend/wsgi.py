import os
from flask import send_from_directory
from app import create_app

# Flask app is created at module level (so Gunicorn sees it)
app = create_app()

# Path to built frontend
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend_dist")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    else:
        return send_from_directory(FRONTEND_DIST, "index.html")

if __name__ == '__main__':
    # Local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
