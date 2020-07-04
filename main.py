#!/usr/bin/env python
# coding: utf-8

import warnings
warnings.filterwarnings("ignore")
import requests
from PIL import Image
import io
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import ssl
options = FirefoxOptions()
#options.add_argument("--headless")
ssl._create_default_https_context = ssl._create_unverified_context


class Scraper:
    def __init__(self,inputs):
        self.inputs = inputs
        
    def link_from_categories(self):
        url_list = []
        for te_in in self.inputs:
            website = "https://www.abcd.com/?q=" + str(te_in)
            url_list.append(website)
        return url_list

    def source_grabber(self,main):
        ext_img_http_urls = [] #list of html page source  # From Selenium
        driver = webdriver.Firefox(options=options)
        for urls in main:
            try:
                driver(urls)
                ext_img_http_urls.append(driver.page_source)
            except:
                continue
        driver.quit()
        return ext_img_http_urls

    def img_link_extractor(self,sources):
        main = []
        for i in sources:
            soup = BeautifulSoup(i)  # link = html source
            # Single Image
            #soup.find('a', {'class':"rel-link"})['href']
            # Multiple Images
            main += ([tag['href'] for tag in soup.find_all('a', {'class':"rel-link"})])
        return main


    def image_downloader(self,img_url: str,pic_length):
        """
        Input:
        param: img_url  str (Image url)
        Tries to download the image url and use name provided in headers. Else it randomly picks a name
        """
        print(f'Downloading: {pic_length}')
        res = requests.get(img_url, stream=True)
        count = 1
        while res.status_code != 200 and count <= 5:
            res = requests.get(img_url, stream=True)
            print(f'Retry: {count} {img_url}')
            count += 1
        # checking the type for image
        if 'image' not in res.headers.get("content-type", ''):
            print('ERROR: URL doesnot appear to be an image')
            return False
        # Trying to red image name from response headers
        try:
            image_name = str(img_url[(img_url.rfind('/')) + 1:])
            if '?' in image_name:
                image_name = image_name[:image_name.find('?')]
        except:
            image_name = str(random.randint(11111, 99999))+'.jpg'

        i = Image.open(io.BytesIO(res.content))
        download_location = """PATH TO"""
        i.save(download_location + '/'+image_name)
        return f'Download complete: {pic_length}'

        # def run_downloader(process: int, images_url: list):
        #     """
        #     Inputs:
        #         process: (int) number of process to run
        #         images_url:(list) list of images url
        #     """
        #     print(f'MESSAGE: Running {process} process')
        #     results = ThreadPool(process).imap_unordered(image_downloader, images_url)
        #     for r in results:
        #         print(r)

        # num_process = 10
        # run_downloader(num_process, main)


        # end = time.time()
        # print('Time taken to download {}'.format(len(get_urls())))
        # print(end - start)

    def hit_download(self,main_img_link):
        batchsize = 500
        for i in range(0, len(main_img_link), batchsize):
            batch = main_img_link[i:i+batchsize]
            for j in batch:
                pic_length = [main_img_link.index(j),'/', len(main_img_link)]
                self.image_downloader(j,pic_length)
        return "Success"
    
    
    def classifier_link(self):
        # Page Source
        ext_img_http_urls = self.source_grabber(self.inputs)
        # Media links Regex
        media = self.img_link_extractor(ext_img_http_urls)
        # Actual Download Media
        self.hit_download(media)
        return "Download Complete"
    
    def classifier_caregory(self):
        # Generates Link
        url_list = self.link_from_categories()
        # Page Source
        ext_img_http_urls = self.source_grabber(url_list)
        # Insider Links links Regex
        inside_links = self.source_grabber(ext_img_http_urls)
        # Media links Regex
        media = self.img_link_extractor(inside_links)
	# Actual Download Media
        self.hit_download(media)
        return "Download Complete"


if __name__ == "__main__":
	print("Link // Category")
	input_1 = input()
	if input_1 == "link":
		print("Submit list of Links Here")
		inputs = [item for item in input().split(',')]
		main_obj = Scraper(inputs)
		main_obj.classifier_link()
	else:
		print("Submit list of Categories Here")
		inputs = [item for item in input().split(',')]
		main_obj = Scraper(inputs)
		main_obj.classifier_caregory()
