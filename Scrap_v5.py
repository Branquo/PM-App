import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service

base_url = "https://www.tradingview.com"
data = []

path_to_chromedriver = r"chromedriver/chromedriver.exe"

# Set up the Chrome webdriver with options to run headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")

service = Service(executable_path=path_to_chromedriver)
driver = webdriver.Chrome(service=service, options=options)

def get_element_texts(soup, class_name):
    elements = soup.find_all('div', {'class': class_name})
    return [element.text.strip().replace('\xa0', ' ') for element in elements]

# Loop over all pages of the TradingView strategies
for page in range(250, 498):
    url = f"https://www.tradingview.com/scripts/page-{page}/?script_type=strategies"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    div_boxes = soup.find_all('div', {'class': 'tv-widget-idea__title-row'})

    for div_box in div_boxes:
        # Find the first link in the div box
        link = div_box.find("a")["href"]

        if link.startswith('/'):
            link = base_url + link

        # Load the URL in the webdriver
        driver.get(link)
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "positiveValue-Yvm0jjs7.additionalPercent-Yvm0jjs7")))
            time.sleep(0.5)
        except:
            continue

        print(f"Seite {page}")
        html = driver.page_source
        page_soup = BeautifulSoup(html, 'html.parser')

        # Extract data using BeautifulSoup
        percent_values = get_element_texts(page_soup, 'positiveValue-Yvm0jjs7 additionalPercent-Yvm0jjs7')
        total_closed_trades = get_element_texts(page_soup, 'secondRow-Yvm0jjs7')
        all_stats = percent_values + total_closed_trades

        data.append({
            'Link': link,
            'Net Profit': all_stats[0] if len(all_stats) > 0 else None,
            'Avg Trade': all_stats[1] if len(all_stats) > 1 else None,
            'Profit USD': all_stats[2] if len(all_stats) > 2 else None,
            'Closed Trades': all_stats[3] if len(all_stats) > 3 else None,
            'Percent Profit': all_stats[4] if len(all_stats) > 4 else None,
            'Profit Factor': all_stats[5] if len(all_stats) > 5 else None,
            'Drawdown': all_stats[6] if len(all_stats) > 6 else None,
        })

# Quit the webdriver
driver.quit()

# Create a Pandas DataFrame from the data list
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file in the specified directory
output_path = "Scrap_Final4.xlsx"
df.to_excel(output_path, index=False)