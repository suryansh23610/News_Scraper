import re
import csv
import time
from datetime import datetime, timedelta,date
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
import time


class NewspaperScraper:
    def __init__ (self, dateStart, dateEnd):
        self.searchTerm1 = 'bank'
        self.searchTerm2='coronavirus'
        self.dateStart = parse(dateStart)
        self.dateEnd = parse(dateEnd)
        self.links = []


    def check_dates (self, date):
        page_date = parse(date)
        if page_date >= self.dateStart and page_date <= self.dateEnd:
            return True
        return False


    def write_to_csv (self, data, file_name):
        print ('writing to CSV...')

        keys = data[0].keys()
        with open(file_name, 'a+',encoding='utf-8',newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print('written to file')

            
    def check_keywords(self,s):
        if re.search('coronavirus',s.lower()) is not None or re.search('covid',s.lower()) is not None:
            if re.search('bank',s.lower()) is not None :
                return  True
        return False

    




class CNBCScraper(NewspaperScraper):

    def get_pages (self, sleep_time=3):
        print ('running get_pages()...')

        links = {}
        stop = False
        index = 1
        days = (self.dateEnd.date() - self.dateStart.date()).days + 1

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        
        driver = webdriver.Chrome(options=chrome_options,executable_path=r"C:\Users\suryansh\Downloads\chromedriver_win32 (2)\chromedriver.exe")
        driver.get('http://search.cnbc.com/rs/search/view.html?partnerId=2000'
                            + '&keywords=' + self.searchTerm1
                            + '%2C'
                            + self.searchTerm2
                            + '&sort=date&type=news&source=CNBC.com'
                            + '&pubtime=' + str(days) + '&pubfreq=d'
        )
        time.sleep(15)


        ele=driver.find_element_by_xpath('//select[@class="minimal SearchResults-searchResultsSelect"]')
        ele.find_element_by_xpath(".//option[contains(text(), 'Articles')]").click()
        time.sleep(sleep_time)
       
        for i in range(50):

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            time.sleep(2)

        results=driver.find_elements_by_xpath('//div[@class="SearchResult-searchResult SearchResult-standardVariant"]')

        main_data=[]

        for result in results:
            try:
                pub_date = result.find_element_by_xpath(".//span[@class='SearchResult-publishedDate']").text

                ltext = result.find_element_by_xpath('.//span[@class="Card-title"]').text
                link = result.find_element_by_xpath('.//a[@class="resultlink"]').get_attribute('href')
                print(link)
                if  self.check_keywords(ltext) and not links.get(link,False) and self.check_dates(pub_date):
                    links[link]=True
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(link)
                    time.sleep(10)
                    p=''
                    for para in driver.find_elements_by_xpath('//div[@class="group"]'):
                        for e in para.find_elements_by_xpath('.//p'):
                            p+=e.text
                        
                    data = {
                        'title': ltext,
                        'date_published': pub_date,
                        'article_link': link,
                        'text': p
                    }
                    print(data['title'])
                    main_data.append(data)
                    time.sleep(sleep_time)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(e)

        self.links = links
        return main_data
    
start=input('From date in format yyyy-mm-dd :- ')
end=input(' date in format yyyy-mm-dd :- ')
def run_scraper (start,end):
    scraper=CNBCScraper(start,end)
    data=scraper.get_pages()
    if len(data)==0:
        print('NO news related to current keywords in specified range')
    else:
        scraper.write_to_csv(data,'CNBCScraper.csv')
      
    
run_scraper(start,end)

 
    