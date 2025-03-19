import requests
from bs4 import BeautifulSoup

# URL of the profile
URL = "https://www.duolingo.com/profile/Stijn3s"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_duolingo():
    response = requests.get(URL, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the h4 above the div with "Dagreeks"
    dagreeks_div = soup.find("div", string="Dagreeks")
    if dagreeks_div:
        h4_element = dagreeks_div.find_previous("h4")
        if h4_element:
            print("Text in h4:", h4_element.get_text(strip=True))
        else:
            print("No h4 found above 'Dagreeks'")
    else:
        print("'Dagreeks' not found on the page")

# Run the scraper
scrape_duolingo()
