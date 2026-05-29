import requests
from bs4 import BeautifulSoup

class FawaNewsScraper:
    BASE_URL = "http://www.fawanews.com"

    @staticmethod
    def get_matches():
        try:
            response = requests.get(FawaNewsScraper.BASE_URL)
            response.raise_for_status()
        except Exception as e:
            print("Error fetching website:", e)
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        matches = []

        match_elements = soup.find_all('div', class_='user-item --active')
        for item in match_elements:
            # Match link
            a_tag = item.find('a', href=True)
            match_link = f"{FawaNewsScraper.BASE_URL}/{a_tag['href']}" if a_tag else None

            # Image
            img_tag = item.find('img')
            image_url = img_tag['src'] if img_tag else None

            # Match name
            name_tag = item.find('div', class_='user-item__name')
            match_name = name_tag.text.strip() if name_tag else None

            # Match time and league
            time_tag = item.find('div', class_='user-item__playing')
            match_time = time_tag.text.strip() if time_tag else None

            matches.append({
                'image': image_url,
                'match': match_name,
                'time': match_time,
                'link': match_link
            })

        return matches