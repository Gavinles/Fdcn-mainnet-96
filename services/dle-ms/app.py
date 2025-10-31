from flask import Flask, request, jsonify
from flask_cors import CORS
import socketio as sio_client
import threading
import time

app = Flask(__name__)
CORS(app)

# In-memory cache of account states synchronized with state-ledger
account_cache = {}
sio = sio_client.Client()
connected = False

@sio.event
def connect():
    global connected
    connected = True
    print(">>> Connected to State Ledger <<<")

@sio.event
def disconnect():
    global connected
    connected = False
    print(">>> Disconnected from State Ledger <<<")

@sio.event
def state_update(data):
    """Handle state updates from state-ledger"""
    # State updates are sent to specific rooms (account-specific)
    # Since we join rooms per account, we'll receive updates for accounts we've queried
    # We need to infer which account this update is for based on context
    # For now, we'll store it generically and update when we have better context
    # In production, the state_update event would include an accountId field
    pass

def connect_to_ledger():
    """Connect to the state-ledger WebSocket service"""
    global connected
    time.sleep(2)  # Wait for state-ledger to start
    while True:
        try:
            if not connected:
                print("Attempting to connect to state-ledger...")
                sio.connect('http://state-ledger:5002', wait_timeout=10)
            time.sleep(5)
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(5)

# Start background thread to maintain connection to state-ledger
threading.Thread(target=connect_to_ledger, daemon=True).start()

@app.route('/account/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account state from cache or return default"""
    # If we have cached state, return it
    if account_id in account_cache:
        return jsonify(account_cache[account_id])
    
    # Return default account state if not found
    default_state = {"fex": 0, "su": 0, "staked": 0}
    
    # Try to join the room for this account to receive future updates
    try:
        if connected:
            # Set up a one-time listener for state updates for this specific account
            received_state = {}
            
            def handle_state_update(data):
                # Cache the received state
                received_state['data'] = data
                account_cache[account_id] = data
            
            # Register temporary handler
            sio.on('state_update', handle_state_update)
            
            # Join the room to get the current state
            sio.emit('join', {'accountId': account_id})
            
            # Wait briefly for the initial state response
            time.sleep(0.2)
            
            # If we received state, return it
            if 'data' in received_state:
                return jsonify(received_state['data'])
            
            # Check cache again in case it was updated
            if account_id in account_cache:
                return jsonify(account_cache[account_id])
    except Exception as e:
        print(f"Error joining room: {e}")
    
    # Cache and return default state
    account_cache[account_id] = default_state
    return jsonify(default_state)

@app.route('/transaction', methods=['POST'])
def create_transaction():
    """Forward transaction to state-ledger via WebSocket"""
    try:
        data = request.get_json()
        if connected:
            sio.emit('transaction', data)
            return jsonify({'status': 'success', 'message': 'Transaction submitted'})
        else:
            return jsonify({'error': 'State ledger unavailable'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(">>> DLE (Distributed Ledger Engine) Service: ONLINE <<<")
    app.run(host='0.0.0.0', port=5003)
