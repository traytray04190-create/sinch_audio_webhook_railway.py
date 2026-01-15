#!/usr/bin/env python3
"""
Sinch Audio Webhook Server - Railway Ready Version
This server handles Sinch webhooks for audio file playback.
Deploy this to Railway to get a permanent public URL.
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Audio file URL - can be set via environment variable or query parameter
# Default: empty (will use query parameter from Sinch)
AUDIO_URL = os.environ.get('AUDIO_URL', '')


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    """Handle incoming call and return NCCO (Network Call Control Object) for Sinch"""
    
    # Get audio URL from query parameter (passed by Sinch) or use default
    audio_url = request.args.get('audio_url', AUDIO_URL)
    
    if not audio_url:
        return jsonify({'error': 'No audio URL provided. Set audio_url query parameter or AUDIO_URL environment variable.'}), 400
    
    # Sinch uses NCCO (JSON) instead of TwiML (XML)
    # NCCO is an array of actions to perform during the call
    # For audio files, we use the "stream" action
    ncco = [
        {
            "action": "stream",
            "streamUrl": [audio_url]
        },
        {
            "action": "hangup"
        }
    ]
    
    return jsonify(ncco), 200


@app.route('/event', methods=['POST'])
def event():
    """Handle Sinch call event callbacks"""
    try:
        data = request.get_json() or {}
        event_type = data.get('event', 'unknown')
        call_id = data.get('callId', data.get('id', 'unknown'))
        call_status = data.get('status', data.get('state', 'unknown'))
        call_duration = data.get('duration', 0)
        
        print(f"Sinch Event: {event_type}")
        print(f"Call ID: {call_id}")
        print(f"Status: {call_status}")
        print(f"Duration: {call_duration}s")
    except Exception as e:
        print(f"Error processing event: {str(e)}")
    
    return '', 200


@app.route('/', methods=['GET'])
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'online',
        'service': 'Sinch Audio Webhook',
        'endpoint': '/voice'
    }), 200


@app.route('/set_audio_url', methods=['POST'])
def set_audio_url():
    """Update the audio file URL (if needed)"""
    global AUDIO_URL
    try:
        data = request.get_json() or {}
        AUDIO_URL = data.get('audio_url', AUDIO_URL)
        return {'status': 'success', 'audio_url': AUDIO_URL}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400


if __name__ == '__main__':
    # Get port from Railway environment variable (they provide this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Sinch Audio Webhook Server on port {port}...")
    print(f"Webhook endpoint: /voice")
    print(f"Health check: /")
    
    # Railway expects the server to listen on 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=False)
