from bs4 import BeautifulSoup
import requests
from main import download_video

# Define headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# Fetch the webpage with headers
url = 'https://91porn.com/v.php?category=top&viewtype=basic'
response = requests.get(url, headers=headers)
response.raise_for_status()

# Create a BeautifulSoup object
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)

# Find all the URLs and their associated like and dislike numbers
for div in soup.find_all('div', class_='well well-sm videos-text-align'):
    print(div)
    a_tag = div.find('a')
    if a_tag:
        url = a_tag['href']
        print(f'URL: {url}')
    like_img = div.find('img', src='images/like.png')
    dislike_img = div.find('img', src='images/dislike.png')
    if like_img and dislike_img:
        like_num = like_img.find_next_sibling(text=True).strip()
        dislike_num = dislike_img.find_next_sibling(text=True).strip()
        print("Likes:", like_num)
        print("Dislikes:", dislike_num)
        if dislike_num and like_num and float(dislike_num) / float(like_num) < 0.3:
            print(url)
            #download_video(url, None)
