from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory database simulating the blockchain state
DB = {"accounts": {"0xUserA": {"fex": 1000.0, "su": 50, "staked": 100.0}}}

@socketio.on('join')
def on_join(data):
    account_id = data.get('accountId')
    if account_id: join_room(account_id); emit('state_update', DB['accounts'].get(account_id, {}), room=account_id)

@socketio.on('transaction')
def process_transaction(tx):
    acc_id = tx.get('accountId')
    if not acc_id: return
    if acc_id not in DB['accounts']: DB['accounts'][acc_id] = {"fex": 0, "su": 0, "staked": 0}
    
    if tx.get('type') == 'PoccReward':
        DB['accounts'][acc_id]['fex'] += tx.get('fex_reward', 0)
        DB['accounts'][acc_id]['su'] += tx.get('su_reward', 0)
        emit('state_update', DB['accounts'][acc_id], room=acc_id)

if __name__ == '__main__':
    print(">>> State Ledger Service (Simulation): ONLINE <<<")
    socketio.run(app, host='0.0.0.0', port=5002)
