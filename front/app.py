import streamlit as st
import requests
import os

st.set_page_config(page_title="클래식 기타 레퍼토리 추천기", layout="wide")

if 'step' not in st.session_state:
    st.session_state.step = 'main'
if 'payload' not in st.session_state:
    st.session_state.payload = {}

if st.session_state.step == 'main':
    st.title("클래식 기타 레퍼토리 맞춤 추천기")
    st.write("당신의 연주 고민과 선호하는 스타일을 분석하여 최적의 명곡을 찾아드립니다.")
    st.divider()
    
    st.markdown("### 클래식 기타 레퍼토리를 추천받고 AI 멘토에게 조언도 들어보세요~!")
    st.write("간단한 8가지 질문에 답하고, 현재의 연주 수준과 감성에 딱 맞는 곡을 추천받을 수 있어요.")
    st.write("더불어 AI 기타 멘토가 여러분의 고민에 깊이 공감하고 맞춤형 조언을 제공합니다.")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("곡 추천 및 조언 받기", type="primary", use_container_width=True):
            st.session_state.step = 'questions'
            st.rerun()

elif st.session_state.step == 'questions':
    st.title("당신의 연주 상태를 상세히 알려주세요")
    st.write("아래의 질문에 하나씩 차례대로 답해주세요!")
    st.write("")
    
    proficiency = st.radio("1. 현재 기타 연주 숙련도는?", ["입문", "초급", "중급", "고급"], horizontal=True)
    playing_period = st.radio("2. 기타를 연주한 기간은?", ["6개월 미만", "6개월~1년", "1년~3년", "3년 이상"], horizontal=True)
    biggest_struggle = st.text_input("3. 현재 가장 큰 연주 고민은?", placeholder="예: 운지가 빨리 안 바뀌어요, 아포얀도 톤이 안 예뻐요 등 자유롭게 적어주세요.")
    sight_reading = st.radio("4. 악보 이해도는 어느 정도인가요?", ["타브 악보만 겨우 봄", "오선보를 천천히 읽음", "초견 연주가 어느 정도 가능"], horizontal=True)
    desired_difficulty = st.radio("5. 원하는 곡의 난이도는?", ["쉬움", "적절함", "도전적"], horizontal=True)
    technique = st.radio("6. 집중적으로 연습할 테크닉은?", ["아르페지오", "트레몰로", "스케일", "화음"], horizontal=True)
    mood = st.radio("7. 어떤 분위기의 곡을 원하시나요?", ["경쾌함", "서정적임", "웅장함", "우수에 찬", "남미풍"], horizontal=True)
    length = st.radio("8. 선호하는 곡의 길이는?", ["짧음(3분 미만)", "보통(3~5분)", "긺(5분 이상)"], horizontal=True)

    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("메인으로 돌아가기", use_container_width=True):
            st.session_state.step = 'main'
            st.rerun()
    with col2:
        if st.button("결과 확인하기", type="primary", use_container_width=True):
            if not biggest_struggle.strip():
                st.warning("가장 큰 연주 고민을 짧게라도 입력해 주세요!")
            else:
                st.session_state.payload = {
                    "proficiency": proficiency,
                    "playing_period": playing_period,
                    "biggest_struggle": biggest_struggle,
                    "sight_reading": sight_reading,
                    "desired_difficulty": desired_difficulty,
                    "technique": technique,
                    "mood": mood,
                    "length": length
                }
                st.session_state.step = 'result'
                st.rerun()

elif st.session_state.step == 'result':
    st.title("맞춤 추천 결과 및 AI 멘토링")
    st.divider()
    
    with st.spinner('맞춤형 알고리즘과 AI 멘토가 분석 중입니다...'):
        try:
            api_url = os.environ.get("API_URL", "http://localhost:8000/recommend")
            response = requests.post(api_url, json=st.session_state.payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data["recommendations"]
                llm_comment = data["llm_comment"]
                
                st.info(f"**AI 기타 멘토의 조언:**\n\n{llm_comment}")
                
                if not results:
                    st.warning("조건에 완벽히 맞는 곡이 아직 데이터베이스에 없습니다. 조건을 조금 변경해 보세요!")
                else:
                    st.success("짜잔! 당신을 위한 추천 레퍼토리입니다.")
                    
                    for idx, song in enumerate(results):
                        with st.container(border=True):
                            st.subheader(f"Top {idx+1}. {song['title']} - {song['composer']}")
                            st.write(f"**곡 설명:** {song['description']}")
                            st.link_button("유튜브 연주 영상 보러가기", song['youtube_url'])
            else:
                st.error("백엔드 서버에서 에러가 발생했습니다.")
                
        except Exception as e:
            st.error(f"백엔드 서버와 연결할 수 없습니다. 오류: {e}")
            
    st.divider()
    if st.button("다시 추천받기", use_container_width=True):
        st.session_state.step = 'main'
        st.rerun()