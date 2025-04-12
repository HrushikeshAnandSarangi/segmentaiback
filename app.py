from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from werkzeug.exceptions import BadRequest

class SegmentationHandler:
    @staticmethod
    def process(text):
        """Process text into segments (example: sentence splitting)"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        return sentences

class Config:
    DEBUG = True
    CORS_ORIGINS = "*"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS for all routes
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging
    app.logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    
    return app

app = create_app()

def create_response(data=None, message="", status=200, error=None):
    """Standardized response format"""
    return jsonify({
        "data": data,
        "message": message,
        "status": status,
        "error": error
    }), status
@app.route('/')
def index():
    """Index route"""
    return create_response(message="Welcome to the Segmentation API")
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return create_response(message="Service is running")

@app.route('/segment', methods=['POST'])
def segment_text():
    """Endpoint for text segmentation"""
    try:
        # Validate request content type
        if not request.is_json:
            return create_response(
                error="Invalid content type", 
                message="Request must be JSON",
                status=415
            )
            
        # Parse JSON data
        try:
            data = request.get_json()
        except BadRequest:
            return create_response(
                error="Invalid JSON",
                message="Request contains invalid JSON",
                status=400
            )
        
        # Validate 'text' field
        if 'text' not in data or not isinstance(data['text'], str):
            return create_response(
                error="Validation error",
                message="Text field is required and must be a string",
                status=400
            )
        
        # Process text
        segments = SegmentationHandler.process(data['text'])
        
        return create_response(
            data={"segments": segments},
            message="Text segmented successfully"
        )
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_response(
            error="Internal server error",
            message="An unexpected error occurred",
            status=500
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)