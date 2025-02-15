from util import calculate_aggregate_score,system_prompt_sentiment,predictprice,system_predict,extract_json_from_string
import json
from flask import jsonify

class GroqChatbot:
    def __init__(self, client):
        self.client = client

    def chat(self, query: str):
        # print(query)
        answer = self.client.perform_action(
            connection="groq",
            action="generate-text",
            params=[
                query,
                "system prompt"
            ]
        )

        if not answer or "result" not in answer:
            return {"error": "Failed to fetch response from Groq."}

        return answer["result"]
    
    
    
    def trending_coins(self,tweets:list):
        SystemPrompt = '''
                                Task:
                                Extract cryptocurrency mentions from the tweet below.
                                Identify both the full name and ticker symbol when available.
                                If only one is present, infer the missing part using common crypto knowledge.

                                Rules:
                                If only the ticker (e.g., "ETH") is mentioned, convert it into the full name (e.g., "Ethereum").

                                Output:
                                    only full name of crypto currency in json format!!!
                                    example:
                                        {"cryptocurrencies": ["Bitcoin"]}
                        '''
        query = " ".join(tweets)
        trends = self.client.perform_action(
            connection="groq",
            action="generate-text",
            params=[
                query,
                SystemPrompt
            ]
        )
        
        if not trends or "result" not in trends:
            return {"error": "Failed to fetch response from Groq."}

        response= trends["result"]
        if isinstance(response, str):
            try:
                response=extract_json_from_string(response)
                response = json.loads(response)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON response from bot.trending_coins"}), 400    
    
    
    
    def sentiment_coins(self,coin:str,t:int,query:list):
        coin_name=coin
        SystemPrompt=system_prompt_sentiment(coin_name)
        SystemPrompt+='''Output:
                            Only sentiment and confidence in Json format nothing else ./
                            example:
                                {"sentiment": "positive", "confidence": 80}
                    '''
        # print(SystemPrompt)
        i=0
        sentiments=[]
        for tweet in query:
            i=i+1
            coins=self.client.perform_action(
                connection="groq",
                action="generate-text",
                params=[
                    tweet,
                    SystemPrompt
                ]
            )
            response=coins['result']
            print(f"index is {i} and {response}")
            try:
                response = json.loads(response)
                sentiments.append(response)
            except json.JSONDecodeError:
                print('INVALID JSON')
        sentiment_score= calculate_aggregate_score(sentiments)
        predicted_price=predictprice(coin,t)
        print(predicted_price)
        # predicted_price=json.dumps(predicted_price, indent=4, default=str)
        # print(predicted_price)
        prompt=system_predict(coin_name,sentiment_score)
        prompt+='''
        
            Output:
            output only adjusted_price,current_price,predicted_price in Json format, Nothing else.
            example:        
                        "dex_1": {
                            "adjusted_price": 105551.05190932725,
                            "current_price": 96561.6639990985,
                            "predicted_price": 104551.05190932725
                            }
              
            
        
        '''
        price=self.client.perform_action(
                connection="groq",
                action="generate-text",
                params=[
                    json.dumps(predicted_price, indent=4, default=str),
                    prompt
                    
                ]
            )
        # response=price['result']
        # print(response)
        response={}
        try:
            # print(price)
                json_str =  extract_json_from_string(price['result'])
                print(json_str)
                response_data = json.loads(json_str)
                response={"score":sentiment_score,"dex":response_data}
        except json.JSONDecodeError:
            response={"score":sentiment_score,"dex":predicted_price}
            
        return response
        
        
            
                
