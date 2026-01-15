#!/usr/bin/env python3
"""
Simple Flask server to handle Sinch webhooks for audio file playback
This server must be publicly accessible for Sinch to reach it.
For development, use ngrok or similar tunneling service.

Usage:
1. Set the AUDIO_URL environment variable or modify the AUDIO_URL below
2. Run this server: python sinch_audio_webhook.py
3. Use ngrok to expose it: ngrok http 5000
4. Use the ngrok URL as your webhook URL in Sinch dashboard
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Audio file URL - set this to your public audio file URL
# You can also set it via environment variable: export AUDIO_URL="https://your-audio-file-url.com/audio.mp3"
AUDIO_URL = os.environ.get('AUDIO_URL', 'https://drive.usercontent.google.com/download?id=1lpZ4lgJCayZOIynHQDZtcgkr_E1vH4WC&export=download&authuser=3&confirm=t&uuid=00329742-410d-48cb-abf5-361b6f668431&at=ANTm3cwQnDfROOdJoLg0SUqJ0XWl:1768438701320')


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    """Handle incoming call and return NCCO (Network Call Control Object) for Sinch"""
    
    # Get audio URL from query parameter or use default
    audio_url = request.args.get('audio_url', AUDIO_URL)
    
    # Sinch uses NCCO (JSON) instead of TwiML (XML)
    # NCCO is an array of actions to perform during the call
    # For audio files, we use the "stream" action
    ncco = [
        {
            "action": "stream",
            "streamUrl": [audio_url]
        },
        {
            "action": "pause",
            "length": 1
        },
        {
            "action": "hangup"
        }
    ]
    
    return jsonify(ncco), 200


@app.route('/event', methods=['POST'])
def event():
    """Handle Sinch call event callbacks"""
    data = request.get_json()
    
    event_type = data.get('event', 'unknown')
    call_id = data.get('callId', data.get('id', 'unknown'))
    call_status = data.get('status', data.get('state', 'unknown'))
    call_duration = data.get('duration', 0)
    
    print(f"Sinch Event: {event_type}")
    print(f"Call ID: {call_id}")
    print(f"Status: {call_status}")
    print(f"Duration: {call_duration}s")
    print(f"Full data: {data}")
    
    return '', 200


@app.route('/set_audio_url', methods=['POST'])
def set_audio_url():
    """Update the audio file URL"""
    global AUDIO_URL
    data = request.get_json()
    AUDIO_URL = data.get('audio_url', AUDIO_URL)
    return {'status': 'success', 'audio_url': AUDIO_URL}, 200


if __name__ == '__main__':
    print(f"Starting Sinch Audio Webhook Server...")
    print(f"Audio URL: {AUDIO_URL}")
    print(f"Webhook endpoint: http://localhost:5000/voice")
    print(f"Make sure to expose this server publicly using ngrok or similar")
    print(f"Example: ngrok http 5000")
    # Run on all interfaces so it's accessible
    app.run(host='0.0.0.0', port=5000, debug=True)
