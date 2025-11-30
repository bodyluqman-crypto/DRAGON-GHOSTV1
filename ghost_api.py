from flask import Flask, request, jsonify
from datetime import datetime
from utils import logger, APIValidator
from account_handler import SingleAccountPool
from config import Config

app = Flask(__name__)
account_pool = SingleAccountPool()

api_stats = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'successful_ghost_attacks': 0,
    'failed_attacks': 0,
    'main_account': Config.MAIN_ACCOUNT_ID
}

@app.before_request
def before_request():
    api_stats['total_requests'] += 1
    
    if not APIValidator.check_api_status():
        return jsonify({
            'status': 'error',
            'message': 'API has expired. Please contact administrator.'
        }), 403

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': '🚀 DRAGON Ghost API is running',
        'version': '3.0',
        'author': 'DRAGON',
        'account': Config.MAIN_ACCOUNT_ID,
        'endpoints': {
            'ghost_attack': 'GET /ghost?name=GHOST_NAME&team_code=TEAM_CODE',
            'status': 'GET /status'
        }
    })

@app.route('/ghost', methods=['GET'])
def ghost_attack():
    """هجوم الشبح باستخدام GET مع query parameters"""
    try:
        # أخذ البيانات من query parameters
        team_code = request.args.get('team_code')
        ghost_name = request.args.get('name', 'DRAGON Ghost')
        
        if not team_code:
            return jsonify({
                'status': 'error',
                'message': 'Team code is required. Use: /ghost?name=GHOST_NAME&team_code=TEAM_CODE'
            }), 400
        
        if not APIValidator.validate_team_code(team_code):
            return jsonify({
                'status': 'error',
                'message': 'Invalid team code format. Must be at least 6 digits.'
            }), 400
        
        # إرسال الشبح
        success, message = account_pool.send_single_ghost_attack(team_code, ghost_name)
        
        if success:
            api_stats['successful_ghost_attacks'] += 1
            return jsonify({
                'status': 'success',
                'message': message,
                'team_code': team_code,
                'ghost_name': ghost_name,
                'account_used': Config.MAIN_ACCOUNT_ID,
                'timestamp': datetime.now().isoformat(),
                'api_url': 'https://dragon-ghost.vercel.app/ghost'
            })
        else:
            api_stats['failed_attacks'] += 1
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
            
    except Exception as e:
        logger.error(f"Ghost attack error: {e}")
        api_stats['failed_attacks'] += 1
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """حالة النظام"""
    return jsonify({
        'status': 'success',
        'api_name': 'DRAGON Ghost API',
        'version': '3.0',
        'main_account': Config.MAIN_ACCOUNT_ID,
        'stats': api_stats,
        'uptime': str(datetime.now() - api_stats['start_time'])
    })

@app.route('/test', methods=['GET'])
def test_ghost():
    """اختبار إرسال شبح"""
    try:
        team_code = request.args.get('team_code', '2207780')
        ghost_name = request.args.get('name', 'DRAGON_GTX')
        
        success, message = account_pool.send_single_ghost_attack(team_code, ghost_name)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message,
            'test_data': {
                'team_code': team_code,
                'ghost_name': ghost_name,
                'account_used': Config.MAIN_ACCOUNT_ID
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting DRAGON Ghost API v3.0...")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)