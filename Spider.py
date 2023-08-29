import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Pool

visited_pages = set()

def download_image(url, folder):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = os.path.join(folder, url.split("/")[-1])
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def process_page(url_folder):
    url, folder = url_folder
    try:
        if url in visited_pages:
            return

        visited_pages.add(url)

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for img_tag in soup.find_all('img'):
                img_url = img_tag.get('src')
                if img_url:
                    img_url = urljoin(url, img_url)
                    download_image(img_url, folder)

            for link in soup.find_all('a'):
                link_url = link.get('href')
                if link_url and link_url.startswith(url):
                    process_page((link_url, folder))

            for button in soup.find_all('button'):
                button_url = button.get('data-url') or button.get('onclick')
                if button_url:
                    button_url = urljoin(url, button_url)
                    process_page((button_url, folder))
    except Exception as e:
        print(f"Error crawling {url}: {e}")

if __name__ == "__main__":
    target_url = input("Enter the URL to crawl: ")
    download_folder = input("Enter the folder to save images: ")

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    pool = Pool(processes=4)  # You can adjust the number of processes as needed
    pool.map(process_page, [(target_url, download_folder)])

    print("Crawling and image downloading completed!")
