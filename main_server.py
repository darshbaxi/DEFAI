import os
import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.server.client import ZerePyClient
from src.connections.sonic_connection import SonicConnection
from src.connections.groq_connection import GroqConnection
from groq import GroqChatbot
# You might need to import json if necessary
import json

# ---- Common Initialization Code ----
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

# ---- Flask App (Server Mode) ----
def create_app():
    app = Flask(__name__)
    CORS(app)

    client = ZerePyClient("http://0.0.0.0:8000/")
    initializer = Initializer(client)
    bot = GroqChatbot(client)

    @app.route('/chat', methods=['POST'])
    def chatbot():
        json_data = request.get_json()
        print(json_data)
        if 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = json_data['query']
        print(query)
        response = bot.chat(query)
        return jsonify({"result": response})

    @app.route('/trending_coin', methods=['POST'])
    def personalized_trending_coins():
        json_data = request.get_json()
        print(json_data)
        if 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = json_data['query']
        print(query)
        response = bot.trending_coins(query)
        return jsonify({"result": response})

    @app.route('/sentiment', methods=['POST'])
    def sentiments():
        json_data = request.get_json()
        print(json_data)
        coin = json_data.get("coin")
        t = json_data.get("time")
        tweets = json_data.get("query")
        print(coin)
        return jsonify({"result": bot.sentiment_coins(coin, t, tweets)})

    return app

# ---- CLI Mode ----
def run_cli():
    from src.cli import ZerePyCLI
    cli = ZerePyCLI()
    cli.main_loop()

# ---- Main Entry Point ----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ZerePy - AI Agent Framework')
    parser.add_argument('--server', action='store_true', help='Run in server mode')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=int(os.environ.get("PORT", 5000)),
                        help='Server port (default: value of PORT env var or 5000)')
    args = parser.parse_args()

    if args.server:
        app = create_app()
        app.run(host=args.host, port=args.port, debug=False)
    else:
        run_cli()
