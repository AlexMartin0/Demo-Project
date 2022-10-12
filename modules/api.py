import tweepy
import ssl
import urllib.request
import requests
import json
import re

## API KEY
TWITTER_TOKEN = ""
CLINET_ID_NAVER_API = ""
CLINET_SECRET_NAVER_API = ""
CLINET_ID_NAVER_CLOVA = ""
CLINET_SECRET_NAVER_CLOVA = ""

class TwitterApi:
    def __init__(self):
        self.api = tweepy.Client(bearer_token=TWITTER_TOKEN)

    def get_tweets(self, search_words, counts=30):
        query = '{} -is:retweet lang:ko -has:links -has:images -has:hashtags'.format(search_words)
        tweets = self.api.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                             max_results=counts).data
        tweets_list = []
        for tweet in tweets:
            ## 문자열 데이터 클랜징
            cleaned_tweet = re.sub('[a-zA-z]', '', tweet.text)
            cleaned_tweet = re.sub('[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', '', cleaned_tweet)
            cleaned_tweet = ' '.join(cleaned_tweet.split())
            tweets_list.append(cleaned_tweet)
        return tweets_list

class NaverApi:
    def __init__(self):
        self.url_senti = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
        self.url_image = "https://openapi.naver.com/v1/search/image?query="

    ## 감정분석 결과 가져오기
    def get_sentiment(self, input_text):
        url = self.url_senti
        headers = {
            "X-NCP-APIGW-API-KEY-ID": CLINET_ID_NAVER_CLOVA,
            "X-NCP-APIGW-API-KEY": CLINET_SECRET_NAVER_CLOVA,
            "Content-Type": "application/json"
        }
        content = input_text
        data = {
            "content": content
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        rescode = response.status_code

        if (rescode == 200):
            pass
        else:
            print("Error : " + response.text)

        data = json.loads(response.text)
        # print(data)
        judge, judge_msg = data['sentences'][0]['confidence'], data['sentences'][0]['sentiment']
        negative_score, positive_score, neutral_score = judge['negative'], judge['positive'], judge['neutral']

        return judge_msg, negative_score, positive_score, neutral_score

    ## 네이버 이미지 가져오기
    def get_image(self, store_name, counts=1):
        try:
            context = ssl._create_unverified_context()
            encText = urllib.parse.quote(store_name)
            url = self.url_image + encText + "&display={}&start=1&sort=sim".format(counts)
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", CLINET_ID_NAVER_API)
            request.add_header("X-Naver-Client-Secret", CLINET_SECRET_NAVER_API)
            response = urllib.request.urlopen(request, context=context)
            rescode = response.getcode()

            if rescode == 200:
                response_body = response.read()
                res = response_body.decode('utf-8')
            else:
                print("Error Code:" + rescode)

            data = json.loads(res)

            # 가게이름 100% 일치하지 않으면 가장 첫번째 이미지 리턴
            return data["items"][0]["link"]

        except:
            return None
