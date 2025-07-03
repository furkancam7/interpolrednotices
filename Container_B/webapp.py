
import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from database import db_manager, get_db
from models import RedNotice

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')


@app.route('/')
def index():
    """Main page showing red notices"""
    try:
        session = db_manager.get_session()
        if session:
            red_notices = session.query(RedNotice).order_by(RedNotice.created_at.desc()).all()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            updated_count = session.query(RedNotice).filter(
                RedNotice.updated_at > RedNotice.created_at
            ).count()
            
            return render_template(
                'index.html',
                red_notices=red_notices,
                current_time=current_time,
                updated_count=updated_count,
                total_count=len(red_notices)
            )
        else:
            return render_template('error.html', message="Database connection failed")
            
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('error.html', message="An error occurred")


@app.route('/api/red-notices')
def api_red_notices():
    """API endpoint for red notices data"""
    try:
        session = db_manager.get_session()
        if session:
            red_notices = session.query(RedNotice).order_by(RedNotice.created_at.desc()).all()
            return jsonify([notice.to_dict() for notice in red_notices])
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        logger.error(f"Error in API route: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        session = db_manager.get_session()
        if session:
            count = session.query(RedNotice).count()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'records_count': count,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal server error"), 500


if __name__ == '__main__':
    try:
        db_manager.create_tables()
        logger.info("Database initialized")
        
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
    finally:
        
        db_manager.close_session()
        db_manager.close_engine()
