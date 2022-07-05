import requests
import json
from .models import *
from requests.auth import HTTPBasicAuth

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    #kwargs = json.dumps(kwargs)
    print("GET from {} ".format(url))
    #print("with from {} ".format(kwargs))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dbs"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], state=dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **dealerId)
    
    if json_result:

        reviews = json_result["body"]["data"]["docs"]

        for review in reviews:

            sentiment = analyze_review_sentiments(review['review'])

            # Create a DealerReview object
            review_obj = DealerReview(car_make = review['car_make'], car_model = review['car_model'],
                                      car_year = review['car_year'], dealership = review['dealership'],
                                      id = None, name = review['name'], purchase = review['purchase'],
                                      purchase_date = review['purchase_date'], review = review['review'],
                                      sentiment = sentiment)

            results.append(review_obj)

    return results

def get_dealer_by_id_from_cf(url, dealerId):

    results = []

    # Call get_request with a URL parameter
    json_result = get_request(url, **dealerId)

    if json_result:
        # Get the row list in JSON as dealers
        results = json_result['body']['data']['docs'][0]

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text): 

    url = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/f2e7cab7-454c-4db7-9b9b-18af4c18f0dd" 
    api_key = "EU2BNHgrjTiUhl4MmGOeeSBFIS5_dIZfTfgrjorBKmg0" 

    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 

    response = natural_language_understanding.analyze(text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result() 

    label=json.dumps(response, indent=2) 

    label = response['sentiment']['document']['label'] 

    return(label) 


