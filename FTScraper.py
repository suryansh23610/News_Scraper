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
        self.dateStart = dateStart
        self.dateEnd = dateEnd



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

    




class FTScraper(NewspaperScraper):

    def get_pages (self, sleep_time=3):
        print ('running get_pages()...')

        links = {}
        stop = False
        index = 1

        
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        
        driver = webdriver.Chrome(options=chrome_options,executable_path=r"C:\Users\suryansh\Downloads\chromedriver_win32 (2)\chromedriver.exe")
        url1='https://www.ft.com/search?q=bank%2Ccoronavirus'
        url3='&dateTo='+self.dateEnd+'&dateFrom='+self.dateStart+'&sort=relevance&expandRefinements=true'
        driver.get(url1+url3)
        time.sleep(15)
       

        pages=driver.find_element_by_xpath("//div[@class='search-results__pagination']")
        page_no=pages.find_element_by_xpath("//span[@class='search-pagination__page']").text
        l=page_no.split(' ')
        page=int(l[-1])
        print(page)

        
        main_data=[]
        i=1
        while i<=page:


            if i>=2:
                driver.execute_script("window.open('');")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                url2='&page='+str(i)
                driver.get(url1+url2+url3)
                time.sleep(10)

            big_elems=driver.find_element_by_xpath("//ul[@class='search-results__list']")
            results=big_elems.find_elements_by_xpath(".//div[@class='o-teaser__content']")


            for result in results:
                try:
                    pub_date = result.find_element_by_xpath(".//time[@class='o-teaser__timestamp-date']").text
                    elem=result.find_element_by_xpath('.//div[@class="o-teaser__heading"]').find_element_by_xpath('.//a[@class="js-teaser-heading-link"]')
                    ltext = elem.text
                    summary=result.find_element_by_xpath('.//p[@class="o-teaser__standfirst"]').find_element_by_xpath('.//span').text
                    link = elem.get_attribute('href')
                    print(link)
                    if  self.check_keywords(summary) and not links.get(link,False) :
                        links[link]=True
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(link)
                        time.sleep(5)
                        p=''
                            
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

            i+=1
        return main_data
    

def run_scraper (start,end):
    scraper=FTScraper(start,end)
    data=scraper.get_pages()
    if len(data)==0:
        print('NO news related to current keywords in specified range')
    else:
        scraper.write_to_csv(data,'FTScraper.csv')
      
start='2020-03-31'
end='2020-04-01'
run_scraper(start,end)

 
    