from flask import Flask
from flask_cors import CORS
from routes import api

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return {"message": "Threat Intelligence Dashboard API", "status": "running"}

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Threat Intelligence Dashboard API...")
    print("="*70)
    print("📡 API running on http://localhost:5000")
    print("📊 Frontend should run on http://localhost:5173")
    print("🔧 Press CTRL+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
