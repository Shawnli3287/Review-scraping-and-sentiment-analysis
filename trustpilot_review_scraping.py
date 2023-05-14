import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import pandas as pd


def get_information(url):
    ''' 
    This function will get the information through the respone from
    trustpilot url, and it will return the total page of review for
    that company, total number of reviews for that company and the 
    company name.

    Parameters:
        url: string
            The url link for specific company review page in trustpilot
        
    Return:
        total_page_number: int
            The total page of review for the company

        total_review: int
            The total amount of reviews for the company
        
        company: string
            The name of the company
    '''
    first_resp = requests.get(url)
    soup0 = BeautifulSoup(first_resp.content, 'html.parser')
    page_string = soup0.find("script", {"id": "__NEXT_DATA__"}).string
    jsonObj0 = json.loads(page_string)
    total_page_number = jsonObj0['props']['pageProps']['filters']['pagination']['totalPages']
    total_review = jsonObj0['props']['pageProps']['businessUnit']['numberOfReviews']
    company_string = soup0.find(
        "script", {"data-business-unit-json-ld": "true"}).string
    jsonObj1 = json.loads(company_string)
    company = jsonObj1['@graph'][6]['name']
    return total_page_number, total_review, company


total_page, number_reviews, company_name = get_information(
    'https://ca.trustpilot.com/review/smokehouse.com?languages=all')
print('Total review page for this company is: ', total_page)
print('Total reviews is: ', number_reviews)

'''create the list for different elements'''
company_names = []
date_published = []
rating_value = []
review_boby = []

'''If I use totalPageNumber to scrap all the reviews will recive error:
[<html><body>We have received an unusually large amount of requests from your IP so you have been rate limited</body></html>, '\n'],
so here I only scrap first 200 pages reviews'''

for i in range(1, 50):
    url = "https://ca.trustpilot.com/review/smokehouse.com?languages=all&page={}".format(
        i)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    jsonString = soup.find("script",
                           {"data-business-unit-json-ld": "true"}).string
    jsonObject = json.loads(jsonString)

    for i in range(len(jsonObject['@graph'])):
        if jsonObject['@graph'][i]['@type'] == 'Review':
            company_names.append(company_name)
            date_published.append(jsonObject['@graph'][i]['datePublished'])
            rating_value.append(
                jsonObject['@graph'][i]['reviewRating']['ratingValue'])
            review_boby.append(jsonObject['@graph'][i]['reviewBody'])

'''turn all list into a dataframe'''
df = pd.DataFrame(list(zip(company_names,
                           date_published,
                           rating_value,
                           review_boby)),
                  columns=['companyName',
                           'datePublished',
                           'ratingValue',
                           'reviewBoby'])

'''Turn DataFrame into csv and download to computer'''
df.to_csv('Review_result.csv', encoding='utf-8')
