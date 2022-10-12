from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd


class MakeRecommendations:
    def __init__(self):
        self.okt = Okt()
        self.tfidf = TfidfVectorizer()

    ## 형태소 리턴
    def get_token(self, input_text):
        tokens = self.okt.pos(input_text)

        token_bow = ''
        for token in tokens:
            word, part = token[0], token[1]
            if (part == 'Noun') or (part == 'Adjective') or (part == 'Verb') or (part == 'Adverb'):  ## 명사, 동사, 형용사 토큰화
                token_bow += '{} '.format(word)

        print(token_bow)
        return token_bow

    ## 코사인 유사도 확인
    def make_cosine_sim(self, dummy, input_text):
        ## df에 input text 추가
        dummy.loc[len(dummy)] = ['my_opinion', input_text]

        ## tfidf 매트릭스 생성
        tfidf_matrix = self.tfidf.fit_transform(dummy['bow'])

        ## 코사인 유사도 생성
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        ## 가게별 인덱스 저장
        indices = pd.Series(dummy.index, index=dummy['store'])

        ## df에 추가한 input text 삭제
        dummy.drop(dummy.index[-1], inplace=True)

        ## 최종값 리턴
        return indices, cosine_sim

    ## 코사인 유사도 상위 10개값 리턴
    def get_recommendations(self, dummy, cosine_sim, indices, counts=10):
        idx = indices['my_opinion']
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:counts + 1]
        store_indices = [i[0] for i in sim_scores]
        return list(dummy['store'].iloc[store_indices]), sim_scores
