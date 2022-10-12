import streamlit as st
import random


def write_down(color, text, font_size=12):
    error = '<p style="font-family:sans-serif; color:{}; font-size: {}px;">{}</p>'.format(color, font_size, text)
    st.markdown(error, unsafe_allow_html=True)


def random_sentiment_text(sentiment_type):
    negative_text = ['우울한 날엔 맛있는 음식 먹어야죠!', '안좋은 일 있으신가봐요?', '부정적인 마음을 버려요~', '웃음이 필요하시군요?', '힘든일 있으신가봐요.']
    positive_text = ['기분 좋은 날~', '최고의 기분으로 맛있는 음식 먹어볼까요?', '돌빼곤 뭐든 먹을 수 있는 기분이시군요.', '기분 좋은 날 친구와 시원한 맥주 한잔 어때요?',
                     '신나는 하루를 맛있는 음식과!']
    neutral_text = ['오늘 기분 그저 그렇죠?', '괜찮으세요?', '아무 생각 없을때가 가끔은 좋더라구요', '정처없이 맛집을 향해 걸어봐요~', '무념무상']

    random_no = random.randrange(0, 5)
    if sentiment_type == 'negative':
        return negative_text[random_no]
    elif sentiment_type == 'positive':
        return positive_text[random_no]
    elif sentiment_type == 'neutral':
        return neutral_text[random_no]
