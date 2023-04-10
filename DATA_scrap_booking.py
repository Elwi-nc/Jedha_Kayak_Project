# Import os => Library used to easily manipulate operating systems
## More info => https://docs.python.org/3/library/os.html
import os 

# Import logging => Library used for logs manipulation 
## More info => https://docs.python.org/3/library/logging.html
import logging

# Import scrapy and scrapy.crawler 
import scrapy
from scrapy.crawler import CrawlerProcess

class booking_spider(scrapy.Spider):

    # Name of your spider
    name = 'booking_spider'
    allowed_domain = ['https://www.booking.com']
    # Url to start your spider from 
    
    city_list = ["Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg", "Colmar",
                 "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence",
                 "Avignon", "Uzes", "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz",
                 "Bayonne", "La Rochelle"]
    
    updated_city_list = []
    for city in city_list:
        x = city.replace(' ', '+')
        updated_city_list.append(x)
    
    start_urls = []
    
    for city in updated_city_list:
        urls = f'https://www.booking.com/searchresults.html?aid=304142&ss={city}&order=bayesian_review_score%2F&'
        for page_num in range(0, 20):
            start_urls.append(urls+f'offset={25*page_num}')
    
    def parse(self, response):
        #rows = response.xpath("//div[@class='d20f4628d0']")
        rows = response.xpath("//div[contains(@data-testid,'property-card')]")
        
        #nb_hotels = response.xpath("//div[contains(@class,'d8f77e681c')]")
        city = response.xpath("//input[contains(@class,'ce45093752')]/@value").get()
        #rows = response.xpath("//div[contains(@class,'d4924c9e74')]")
        for row in rows:
            hotel_address = row.xpath(".//span[contains(@data-testid,'address')]/text()").get()
            hotel_name = row.xpath(".//div[contains(@data-testid,'title')]/text()").get()
            hotel_note_name = row.xpath(".//div[contains(@class,'b5cd09854e f0d4d6a2f5')]/text()").get()
            hotel_note_nbr = row.xpath(".//div[contains(@class,'b5cd09854e d10a6220b4')]/text()").get()
            hotel_note_nbr_review = row.xpath(".//div[contains(@class,'d8eab2cf7f c90c0a70d3 db63693c62')]/text()").get()
            hotel_link = row.xpath(".//h3[contains(@class,'a4225678b2')]/a/@href").get()
            hotel_desc = row.xpath(".//div[@class='d8eab2cf7f']/text()").get()
            
            yield response.follow(url=hotel_link, callback=self.parse_details, 
                meta={
                    'hotel_city': city,
                    'hotel_name': hotel_name,
                    'hotel_address': hotel_address,
                    'hotel_note_name': hotel_note_name,
                    'hotel_note_nbr': hotel_note_nbr,
                    'hotel_note_nbr_review': hotel_note_nbr_review,
                    'hotel_link': hotel_link,
                    'hotel_desc': hotel_desc}
                    )

    def parse_details(self, response):
        hotel_city = response.request.meta['hotel_city']
        hotel_name = response.request.meta['hotel_name']
        hotel_address = response.request.meta['hotel_address']
        hotel_note_name = response.request.meta['hotel_note_name']
        hotel_note_nbr = response.request.meta['hotel_note_nbr']
        hotel_note_nbr_review = response.request.meta['hotel_note_nbr_review']
        hotel_link = response.request.meta['hotel_link']
        hotel_desc = response.request.meta['hotel_desc']

        latlng = response.xpath(".//div[contains(@class,'hotel-sidebar-map')]/a/@data-atlas-latlng").get()
        #hotel_address = response.xpath(".//span[contains(@class,'address')]/text()").get()
        latlon = latlng.split(",")
        lat = latlon[0]
        lon = latlon[1]

        yield { 
            'hotel_city' : hotel_city,
            'hotel_name': hotel_name,
            'hotel_address' : hotel_address,
            'hotel_note_name' : hotel_note_name,
            'hotel_note_nbr' : hotel_note_nbr,
            'hotel_note_nbr_review' : hotel_note_nbr_review,
            'hotel_link' : hotel_link,
            'hotel_desc': hotel_desc,
            'hotel_lat' : lat,
            'hotel_lon' : lon,
            }
            
# Name of the file where the results will be saved
filename = "scrap_booking.csv"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('src/'):
        os.remove('src/' + filename)
 
# Declare a new CrawlerProcess with some settings
## USER_AGENT => Simulates a browser on an OS
## LOG_LEVEL => Minimal Level of Log 
## FEEDS => Where the file will be stored 
## More info on built-in settings => https://docs.scrapy.org/en/latest/topics/settings.html?highlight=settings#settings
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename : {"format": "csv"},
    }
})

AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# avec crawler process on peut choisir de runner en python, en jason, csv ... 
# commandes listées dans le fichier donné sur le drive

process.crawl(booking_spider)
process.start()

#stop_after_crawl=False