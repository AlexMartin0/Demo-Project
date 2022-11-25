from modules import etc as ec, recoms, api
import pandas as pd
import streamlit as st

# api 객체 선언
naver_api = api.NaverApi()
twitter_api = api.TwitterApi()

# 추천 객체 선언
get_recoms = recoms.MakeRecommendations()

# dummy data 불러오기
dummy = pd.read_excel('excel_files/dummy_token.xlsx')

# 기본 레이아웃 설정
st.set_page_config(layout='centered')
st.header('맛집의 ')

# main 기능 컴포넌트 정의
main_col1, main_col2 = st.columns(2)
with main_col1:
    with st.form('recommendation_form'):
        input_sentence = st.text_input(label='현재의 기분이나 일상을 적어주세요.', help='입력된 텍스트에 따라 인공지능에 의해 맛집이 추천됩니다.',
                                       max_chars=500)
        recommendation_button = st.form_submit_button('추천')
with main_col2:
    with st.form('fight_form'):
        first_food = st.text_input(label='대결할 음식 1', help='두 음식 태그로 실시간 트윗을 수집하여 AI 긍정, 부정 평가를 통해 대결합니다.',
                                   max_chars=10)
        second_food = st.text_input(label='대결할 음식 2', max_chars=10)
        fight_button = st.form_submit_button('대결')

# 추천 버튼
def click_recoms_button(sentence, max_image_cnt=10):
    ## 10자 미만 예외처리
    if len(sentence) <= 10:
        error_msg = '10자 이상으로 작성 바랍니다.'
        ec.write_down('red', error_msg, font_size=12)
        return

    else:
        ## 입력된 문장 NAVER CLOVA API로 감정분석
        sentiment_result = naver_api.get_sentiment(sentence)
        sentiment = sentiment_result[0]
        n_score = round(sentiment_result[1] * 100, 2)
        p_score = round(sentiment_result[2] * 100, 2)
        ne_score = round(sentiment_result[3] * 100, 2)

        ## 감정분석 Case별 분기
        if sentiment == 'negative':
            score = '(긍정: {}% 부정: {}% 중립: {}%)'.format(p_score, n_score, ne_score)
            ec.write_down('red', ec.random_sentiment_text('negative'), font_size=18)

        elif sentiment == 'positive':
            score = '(긍정: {}% 부정: {}% 중립: {}%)'.format(p_score, n_score, ne_score)
            ec.write_down('blue', ec.random_sentiment_text('positive'), font_size=18)

        elif sentiment == 'neutral':
            score = '(긍정: {}% 부정: {}% 중립: {}%)'.format(p_score, n_score, ne_score)
            ec.write_down('blue', ec.random_sentiment_text('neutral'), font_size=18)

        ## 최종 결과 텍스트 출력
        ec.write_down('gray', score, font_size=12)

        ## 코사인 유사도 및 추천 리스트 가져오기
        sentence_token = get_recoms.get_token(sentence)
        indices, cosine_sim = get_recoms.make_cosine_sim(dummy, sentence_token)
        recommendations, cosine_scores = get_recoms.get_recommendations(dummy, cosine_sim, indices, counts=max_image_cnt)

        ## NAVER API로 이미지 불러오기
        image_list, cosine_sim_list = [], []
        for i in range(len(recommendations)):
            link = naver_api.get_image(recommendations[i])

            if link is not None:
                image_list.append(link)
            ## 이미지 link가 없는 Case
            else:
                ## 이미지 없는 경우 → '대학로' 제거 후 호출
                if recommendations[i][-3:] == '대학로':
                    link = naver_api.get_image(recommendations[i][:-3])
                    image_list.append(link)

            cosine_sim_list.append(round(cosine_scores[i][1] * 100, 2))

        ## col 생성 후 이미지 뿌려주기
        with st.form('image_form'):
            cnt = 0
            for i in range(0, int(max_image_cnt / 2)):

                ## 코사인 유사도가 0인 Case가 나오는 경우 break 처리
                if cosine_sim_list[cnt] == 0:
                    break

                ## 코사인 유사도가 0인 Case가 나오는 경우 break 처리
                cols = st.columns(2)
                for col in cols:
                    if cosine_sim_list[cnt] == 0:
                        break

                    ## 가게 이름 뒤에 3자리가 "대학로"인 경우 제거
                    store_name = recommendations[cnt]
                    if store_name[-3:] == '대학로':
                        store_name = store_name[:-3]

                    ## 코사인 유사도 %로 출력
                    col.write(store_name + ' ' + '({}%)'.format(cosine_sim_list[cnt]))

                    ## 사진이 정상적으로 있는 Case
                    if image_list[cnt] is not None:
                        col.image(image_list[cnt], width=300)
                        cnt += 1

            st.form_submit_button('reset')

        # 전체 추천 리스트들의 유사도가 0인 경우
        if sum(cosine_sim_list) == 0:
            error_msg = '애석하게도 추천드릴 곳이 없네요. 다시 작성해주시겠어요?'
            ec.write_down('red', error_msg, font_size=12)

# 대결 버튼
def click_fight_button(food_1, food_2, tweet_counts=30):
    ## 대결할 음식 input이 공란인 Case
    if (food_1 == '') or (food_2 == ''):
        error_msg = '대결할 음식을 입력해주세요.'
        ec.write_down('red', error_msg, font_size=12)
        return

    else:
        food_1_tweets = twitter_api.get_tweets('{}'.format(food_1), counts=tweet_counts)
        food_2_tweets = twitter_api.get_tweets('{}'.format(food_2), counts=tweet_counts)

        ## 각 음식에 대한 트윗의 감정분석 결과값을 담을 리스트 선언
        food_1_result, food_2_result = list(), list()

        ## 입력값에 대한 트위터 스트림이 존재하지 않는 Case 분기
        if len(food_1_tweets) == 0:
            ec.write_down('red', '{}는 자료가 없습니다. 다른 음식을 입력해주세요.'.format(food_1), font_size=16)
            return

        elif len(food_2_tweets) == 0:
            ec.write_down('red', '{}는 자료가 없습니다. 다른 음식을 입력해주세요.'.format(food_2), font_size=16)
            return

        else:

            ## food_1 에 대한 감정분석 결과 리스트 적재
            for tweet in food_1_tweets:
                if tweet not in food_1_result:
                    sentiment_judge = naver_api.get_sentiment(tweet)[0]
                    food_1_result.append(sentiment_judge)
                    print('[{}] 평가: {}  의견: {}'.format(food_1, sentiment_judge, tweet))

            ## food_2 에 대한 감정분석 결과 리스트 적재
            for tweet in food_2_tweets:
                if tweet not in food_2_result:
                    sentiment_judge = naver_api.get_sentiment(tweet)[0]
                    food_2_result.append(sentiment_judge)
                    print('[{}] 평가: {}  의견: {}'.format(food_2, sentiment_judge, tweet))


            ## food_1에 대한 Score 점수 계산
            if len(food_1_result) == 0:
                food_1_score = 0
            else:
                p_cnt_food_1 = food_1_result.count('positive')
                n_cnt_food_1 = food_1_result.count('negative')
                ne_cnt_food_1 = food_1_result.count('neutral')
                food_1_score = round(p_cnt_food_1 / (p_cnt_food_1 + n_cnt_food_1), 2) * 100

            ## food_2에 대한 Score 점수 계산
            if len(food_2_result) == 0:
                food_2_score = 0
            else:
                p_cnt_food_2 = food_2_result.count('positive')
                n_cnt_food_2 = food_2_result.count('negative')
                ne_cnt_food_2 = food_2_result.count('neutral')
                food_2_score = round(p_cnt_food_2 / (p_cnt_food_2 + n_cnt_food_2), 2) * 100

            ## Food score별 Winner 선정 분기
            if food_1_score > food_2_score:
                winner = food_1
            elif food_1_score < food_2_score:
                winner = food_2
            else:
                winner = '중립기어'

            ## 결과 Layout에 출력
            with st.form('fight_result_form'):

                ## 최종 결과 Case별 분기
                if winner == '중립기어':
                    ec.write_down('gray', '무승부 입니다.', font_size=36)

                else:
                    pass
                    ec.write_down('blue', '승자는 [{}] 입니다.'.format(winner), font_size=36)

                ## 최종 결과 메세지 출력
                ec.write_down('gray', '   [{}] (긍정률: {}% 수집 의견: {})'.format(food_1, round(food_1_score, 2), len(food_1_result)),
                              font_size=12)
                ec.write_down('gray', '   [{}] (긍정률: {}% 수집 의견: {})'.format(food_2, round(food_2_score, 2), len(food_2_result)),
                              font_size=12)

                print('food_1 = 긍정:{} 부정:{} 중립:{}'.format(p_cnt_food_1, n_cnt_food_1, ne_cnt_food_1))
                print('food_2 = 긍정:{} 부정:{} 중립:{}'.format(p_cnt_food_2, n_cnt_food_2, ne_cnt_food_2))

                st.form_submit_button('reset')

    winner_image = naver_api.get_image(winner)
    return winner_image

# 버튼 클릭 Event
if recommendation_button:
    click_recoms_button(input_sentence)

if fight_button:
    st.image(click_fight_button(first_food, second_food, tweet_counts=30))
