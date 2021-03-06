#Caitlin Huang
#caitlinh
#section G

#code from https://www.scrapehero.com/scrape-nasdaq-stock-market-data/
#made some modifications to make this more efficient
#note: This code was only used to get one attribute of the stock 
#class (the company's name)

import numpy
import pandas
from sklearn import preprocessing
from lxml import html
import requests
import json
import argparse
import random
from random import randint
import string

def getHeaders():
    return {"Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection":"keep-alive", "Host":"www.nasdaq.com", 
        "Referer":"http://www.nasdaq.com", "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
        }

def parse_finance_page(ticker):
    key_stock_dict = {}
    headers = getHeaders()
    # Retrying for failed request
    for retries in range(5):
        try:	
            url = "http://www.nasdaq.com/symbol/%s"%(ticker)
            response = requests.get(url, headers = headers, verify=False)
            if response.status_code!=200:
                raise ValueError("Invalid Response Received From Webserver")
            parser = html.fromstring(response.text)
            xpath_head = "//div[contains(@id,'pageheader')]//h1//text()"
            xpath_key_stock_table = \
            '//div[contains(@class,"overview-results")]//div[contains(@class,"table-table")]/div'
            xpath_key = './/div[@class="table-cell"]/b/text()'
            xpath_value = './/div[@class="table-cell"]/text()'
            raw_name = parser.xpath(xpath_head)
            key_stock_table =  parser.xpath(xpath_key_stock_table)
            company_name = \
            raw_name[0].replace("Common Stock Quote & Summary Data","").strip() if raw_name else ''
            # Grabbing and cleaning keystock data
            for i in key_stock_table:
                key = i.xpath(xpath_key)
                value = i.xpath(xpath_value)
                key = ''.join(key).strip() 
                value = ' '.join(''.join(value).split()) 
                key_stock_dict[key] = value
            nasdaq_data = {"company_name":company_name, "ticker":ticker,
                "url":url, "key_stock_data":key_stock_dict
            }
            return nasdaq_data
        except Exception as e:
            print("Failed to process the request, Exception:%s"%(e))