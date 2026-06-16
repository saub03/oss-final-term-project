from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class GuitarInput(BaseModel):
    proficiency: str
    playing_period: str
    biggest_struggle: str
    sight_reading: str
    desired_difficulty: str
    technique: str
    mood: str
    length: str

class RecommendationOutput(BaseModel):
    title: str
    composer: str
    description: str
    youtube_url: str

class FinalResponse(BaseModel):
    recommendations: List[RecommendationOutput]
    llm_comment: str

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "songs.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    SONG_DB = json.load(f)

@app.post("/recommend", response_model=FinalResponse)
async def recommend_repertoire(user_input: GuitarInput):
    scored_songs = []
    
    level_map = {"입문": 1, "초급": 2, "중급": 3, "고급": 4}
    user_level = level_map.get(user_input.proficiency, 1)
    
    for song in SONG_DB:
        score = 0
        song_level = level_map.get(song["difficulty"], 1)
        
        if song_level - user_level >= 2:
            continue 
            
        if user_level <= 2 and song_level <= 2:
            score += 2
        elif user_level >= 3 and song_level >= 3:
            score += 2
            
        if user_input.desired_difficulty == "쉬움" and song_level <= user_level:
            score += 3
        elif user_input.desired_difficulty == "적절함" and song_level == user_level:
            score += 3
        elif user_input.desired_difficulty == "도전적" and song_level == user_level + 1:
            score += 3
            
        if user_input.technique in song["technique"]: score += 2
        if user_input.mood in song["mood"]: score += 2
        if user_input.length == song["length"]: score += 1
            
        if score > 0:
            scored_songs.append({"song": song, "score": score})
            
    scored_songs.sort(key=lambda x: x["score"], reverse=True)
    
    results = []
    for item in scored_songs[:3]:
        s = item["song"]
        results.append(
            RecommendationOutput(
                title=s["title"], composer=s["composer"], 
                description=s["description"], youtube_url=s["youtube_url"]
            )
        )

    if results:
        top_song_title = results[0].title
        prompt = (
            f"사용자는 클래식 기타를 '{user_input.playing_period}' 동안 연주해 온 '{user_input.proficiency}'입니다. "
            f"현재 가장 큰 고민은 '{user_input.biggest_struggle}'이고, 악보는 '{user_input.sight_reading}' 수준으로 읽습니다. "
            f"이 사용자를 위해 '{top_song_title}'를 1순위로 추천했습니다. "
            f"1. 기타 선생님의 입장에서 이 사용자의 고민에 공감하고 응원하는 맞춤형 조언을 작성해 주세요"
            f"2. 그리고 '{top_song_title}'에 맞는 기술적, 감정적 조언을 해주세요"
            f"1. 과 2. 번 형식에 맞춰서 작성해주세요. 형식 당 5문장 이내로 작성"
        )
        try:
            response = await client.aio.models.generate_content(
                model='gemini-3.5-flash', 
                contents=prompt
            )
            llm_comment = response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            llm_comment = "응원합니다! 추천해 드린 곡과 함께 즐거운 기타 연습 되시길 바랍니다."
    else:
        llm_comment = "현재 데이터베이스에 완벽히 일치하는 곡이 없습니다. 조건을 조금 완화해 보시면 어떨까요?"

    return FinalResponse(recommendations=results, llm_comment=llm_comment)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)