import argparse
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.cli import ZerePyCLI
from src.server import start_server
from src.server.client import ZerePyClient
from src.connections.sonic_connection import SonicConnection
from src.connections.groq_connection import GroqConnection
from groq import GroqChatbot
import os
class Initializer:
    def __init__(self, client):
        self.client = client
        self.agents = self.client.list_agents()
        self.client.load_agent("starter")
        self.connections = self.client.list_connections()
        groq_api_key = os.getenv("GROQ_API_KEY")
        sonic_api_key = os.getenv("SONIC_API_KEY")
        self.groq = GroqConnection(config={"model": "llama-3.3-70b-versatile"})
        GroqConnection.configure(self.groq, groq_api_key)

        self.coe = SonicConnection(config={"network": "testnet"})
        SonicConnection.configure(self.coe, sonic_api_key)

def create_app():
    """Initialize and configure the Flask app."""
    app = Flask(__name__)
    CORS(app)

    client = ZerePyClient("http://localhost:8000")
    initializer = Initializer(client)
    bot = GroqChatbot(client)

    @app.route('/chat', methods=['POST'])
    def chatbot():
        json_data = request.get_json()
        if 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = json_data['query']
        response = bot.chat(query)  
        return jsonify({"result": response})
    
    @app.route('/trending_coin', methods=['POST'])
    def personalized_trending_coins():
        json_data = request.get_json()
        if 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = json_data['query']
        response = bot.trending_coins(query)  
        return jsonify({"result": response})

    @app.route('/sentiment', methods=['POST'])
    def sentiments():
        json_data = request.get_json()
        coin = json_data["coin"]
        t = json_data["time"]
        tweets = json_data["query"]
        return jsonify({"result": bot.sentiment_coins(coin, t, tweets)})

    return app

def start_flask():
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ZerePy - AI Agent Framework')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    args = parser.parse_args()

    # Start ZerePy server in a separate thread
    threading.Thread(target=start_server, args=(args.host, args.port), daemon=True).start()

    # Start Flask server
    start_flask()
