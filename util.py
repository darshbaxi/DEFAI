import pandas as pd
from prophet import Prophet
import json
def calculate_aggregate_score(sentiments):
    total_weighted_score = 0
    total_confidence = 0

    for sentiment_data in sentiments:
        sentiment = sentiment_data["sentiment"]
        confidence = sentiment_data["confidence"]

        if sentiment == "positive":
            score = 1
        elif sentiment == "negative":
            score = -1
        else: 
            score = 0

        total_weighted_score += score * confidence
        total_confidence += confidence

    if total_confidence == 0:
        return 0  

    aggregate_score = total_weighted_score / total_confidence
    return round(aggregate_score, 4)


def system_prompt_sentiment(coin:str):
    coin_name = coin 
    SystemPrompt=f'''
            Task: 
                Analyze the sentiment of the following tweet about {coin_name}.
                Classify it as positive, negative, or neutral and provide a confidence score (0-100%).
    
            Rules:
                If the tweet expresses excitement, growth, or optimism of {coin_name}, mark it positive./
                If it contains doubt, loss, or negativity, mark it negative of {coin_name}./
                If it’s neutral or factual, mark it neutral of {coin_name}./
                The confidence score reflects the strength of sentiment./        
        '''
    return SystemPrompt
    
def system_predict(coin:str,score:int):
    SystemPrompt=f'''
        
            You are an advanced financial AI assisting in cryptocurrency price forecasting./
            You will analyze current and predicted price (predicted using Prophet Model) and sentiment score of {coin} is {score} to improve price predictions./
            Higher positive sentiment score may increase the price, while negative sentiment score may decrease it./ 
            Ensure that the effect is realistic and aligns with past market behavior./ 
            Return the adjusted price forecast in a structured JSON format./
            
            
           
        '''
    return SystemPrompt
def predictprice(coin:str,t:int):
    results={}
    for dex in range(1,4):
        df = pd.read_csv(f'Data\{coin}_dex_{dex}.csv')
        df['snapped_at'] = pd.to_datetime(df['snapped_at']).dt.tz_localize(None)
        df = df.rename(columns={'snapped_at': 'ds', 'price': 'y'})
        m = Prophet()
        m.fit(df)
        horizon = int(t)
        future = m.make_future_dataframe(periods=horizon, freq='D')
        forecast = m.predict(future)
        print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon))
        
        current_price = df.iloc[-1]['y']
        predicted_price = forecast.iloc[-1][['ds', 'yhat']].to_dict()
        results[f'dex_{dex}'] = {
            "current_price": current_price,
            "predicted_price": predicted_price
        }

    return results

def extract_json_from_string(s):
    start = s.find('{')  
    end = s.rfind('}')   
    return s[start:end+1] if start != -1 and end != -1 else None 