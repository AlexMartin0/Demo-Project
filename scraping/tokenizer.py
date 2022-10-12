import pandas as pd
from konlpy.tag import Okt

dummy_data = pd.read_excel('excel_files/dummy_data.xlsx')
okt = Okt()

tokenize_pd = pd.DataFrame(columns=['store', 'bow'])

for i in range(len(dummy_data)):
    store = dummy_data['store'][i]
    token_bow = ''
    pos = okt.pos(dummy_data['bow'][i])
    for token in pos:
        word, part = token[0], token[1]
        if (part == 'Noun') or (part == 'Adjective') or (part == 'Verb') or (part == 'Adverb'): ## 명사, 동사, 형용사 토큰화
            token_bow += '{} '.format(word)

    tokenize_pd.loc[i] = [store, token_bow]
    print('{}/{}...tokenizing..{}: {}'.format(i + 1, len(dummy_data), len(pos), token_bow))

tokenize_pd.to_excel('excel_files/dummy_token.xlsx', index=False)