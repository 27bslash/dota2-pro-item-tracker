import scrapy
import os
class matchIdSpider(scrapy.Spider):
  name = 'match_ids'
  start_urls = ['http://www.dota2protracker.com/hero/Jakiro']
  
  os.remove('posts.json')
  def parse(self,response):
    for post in response.css('.info'):
      print(post)
      data = post.css('a::attr(href)').re(r".*opendota.*")
      if data:
        yield {
          'title': data
        }