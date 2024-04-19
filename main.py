import requests
import re
import xml.etree.ElementTree as ET
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from collections import Counter
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

okt = Okt()

url = 'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko'

headers ={
    'User-Agent' : 'Mozilla/5.0',
    'Content-Type' : 'text/html; charset=utf-8'
}

response = requests.get(url, headers=headers)

root_element = ET.fromstring(response.text)
iter_element = root_element.iter(tag="item")

title_list = []
description_list = []
for element in iter_element:
    title_list.append(element.find("title").text)
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    description = element.find("description").text
    description_list.append(hangul.sub("",description))

#print("뉴스제목: ", title_list[0:3])
#print("뉴스요약: ", description_list[0:3])

명사_list = []
for title in title_list:
    for 명사 in okt.nouns(title):
        if len(명사) > 1:
            명사_list.append(명사)

for description in description_list:
    for 명사 in okt.nouns(description):
        if len(명사) > 1:
            명사_list.append(명사)

명사_빈도수_list = Counter(명사_list)
#print(명사_빈도수_list)

# 제외단어 추가
stopwords1 = set(STOPWORDS)
stopwords1.add("뉴스")
stopwords1.add("한겨레")
stopwords1.add("동아일보")
stopwords1.add("조선일보")
stopwords1.add("연합뉴스")
stopwords1.add("매일경제")
stopwords1.add("머니투데이")
stopwords1.add("신문")

# 불용어 제거
for word in list(명사_빈도수_list):
    if word in stopwords1:
        del 명사_빈도수_list[word]

masking_image = np.array(Image.open("bg.png"))

# 워드 클라우드 객체 생성
wc =WordCloud(font_path="/Windows/Fonts/malgun.ttf", background_color='white', mode="RGBA", stopwords=stopwords1, mask=masking_image, width=400, height=400, scale=2.0, max_font_size=250)

# 단어 빈도수 데이터로부터 워드 클라우드 생성
gen = wc.generate_from_frequencies(명사_빈도수_list)

# 워드 클라우드를 이미지 파일로 저장
#wc.to_file(r'뉴스기사 워드 클라우드로 생성.png')

# 이미지 색상에 따라 글자 색상 조정
image_colors = ImageColorGenerator(masking_image)
wc.recolor(color_func=image_colors)

# 워드 클라우드 그리기
plt.figure(figsize=(10, 10))
plt.imshow(gen, interpolation='bilinear')
plt.axis('off')

# 그린 워드 클라우드를 파일로 저장
plt.savefig("뉴스기사 워드 클라우드로 생성.png", bbox_inches='tight', transparent=True)

# 파일로 저장한 워드 클라우드 출력
plt.show()