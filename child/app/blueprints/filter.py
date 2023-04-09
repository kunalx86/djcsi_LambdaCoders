#! /Users/droom/Documents/codeshastra_lambda/nenv/bin/python3 
from flask import Blueprint, request, jsonify
from urllib.parse import urlparse
import requests
from google.cloud import vision
from google.cloud.vision_v1 import types
import requests
from bs4 import BeautifulSoup
import urllib
from google.cloud import language_v1
from google.cloud.language_v1 import types
from bson import ObjectId
from app.models.visits import Visits
from app.models.activity import Activity
from app.models.parents import Parents
from app.models.childrens import Childrens
# from google.cloud import safebrowsing


#export GOOGLE_APPLICATION_CREDENTIALS='newcreds.json'
file_path = './sites.txt'
f=open(file_path, 'r')
filter = Blueprint("filter", __name__)

# def check_safe_browsing(url):
#   client = safebrowsing.Client()
#   threat_list = client.threat_matches_find(url=url)
#   if threat_list.matches:
#       return False
#   else:
#       return True

def check_website(url):
    client = vision.ImageAnnotatorClient()
    response = requests.get(url)
    content_type = response.headers.get('content-type')
    
    if content_type.startswith('image/'):
        # If the URL points to an image, analyze it using the Google Cloud Vision API
        image_content = response.content
        image = vision.Image(content=image_content)
        response = client.safe_search_detection(image=image)
        return response.safe_search_annotation.violence >=2 or response.safe_search_annotation.adult>=2 or response.safe_search_annotation.spoof>=2 or response.safe_search_annotation.medical>=2 or response.safe_search_annotation.racy>=2
    elif content_type.startswith('video/'):
        # If the URL points to a video, analyze it using the Google Cloud Video Intelligence API
        # Note: this requires enabling the Video Intelligence API in your Google Cloud Console and setting up authentication
        # See https://cloud.google.com/video-intelligence/docs/quickstart-client-libraries for more information
        pass
    else:
        # If the URL points to a non-image/non-video resource, return False
        return False
      
def image_parser(url):
  r = requests.get(url) 
  htmldata=r.text 
  soup = BeautifulSoup(htmldata, 'html.parser') 
  for item in soup.find_all('img'):
      if item['src'].find('gif')!=-1 or item['src'].find('http')==-1:
        continue
  
      result=check_website(item['src'])
      
      if result:
        # print(item['src'])
        return True
      else:
          return False
          
          
def read_file_into_list(f):
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    return lines


def is_in_blocked_list(url, blocked_list):
    parsed_url = urlparse(url)
    for fqdn in blocked_list:
        if parsed_url.netloc == fqdn:
            return True
    return False

def nlp_website(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)

    content = response.content
    # Make a request to the website and retrieve the text content

    content = response.content

    # Initialize the Natural Language API client
    client = language_v1.LanguageServiceClient()

    # Analyze the content for sentiment and entity recognition
    document = language_v1.Document(content=content, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_sentiment(request={'document': document})
    sentiment = response.document_sentiment.score

    response = client.analyze_entities(request={'document': document})
    entities = [entity.name for entity in response.entities]
    #print(entities)
    # Check if any of the entities are flagged as sensitive
    
    sensitive_list=[]
    sensitive_entities = ["drugs", "alcohol", "gambling", "violence","sex","rape"]
    for entity in entities:
        if entity.lower() in sensitive_entities:
            sensitive_list.append(entity)
            # return True

    # Check if the sentiment score is below a certain threshold
    if sentiment < -0.5:
        return True

    # If no sensitive content is detected, return False
    return False

@filter.route("/checkurl", methods=["POST"])
def check_url():
    
    # url='https://www.instagram.com/stories/bhand.engineer/3075886021175968821/'
    # url='https://stackoverflow.com/questions/61641533/javascript-how-to-check-for-url-with-specific-domain-name'
    
    data = request.json
    url = data["url"]
    
    parent=Parents.objects(_id=ObjectId(data["parent"])).first()
    child=Childrens.objects(_id=ObjectId(data["child"])).first()

    blocked_list = read_file_into_list(f)

    
    blocked = is_in_blocked_list(url, blocked_list)
    
    inappropriate = image_parser(url)
    
    slur = nlp_website(url)
    
    
    visit = Visits(url=url,isblocked=blocked,suggestBlocked=(inappropriate or slur),childrens=ObjectId(data["child"])).save()
    print(child.pk)
    activity = Activity.objects(parent=ObjectId(parent.pk),child=ObjectId(data["child"])).first()
    if activity is None:
      Activity(parent=ObjectId(parent.pk),child=ObjectId(data["child"]),visits=[visit.pk]).save()
    else:
      print(activity)
      existing_visits=activity["visits"]  
      existing_visits.append(vision)
      Activity(parent=ObjectId(data["parent"]),child=ObjectId(data["child"])).update_one(
        visits=existing_visits
      )
     
      
      
    if blocked:  
      return jsonify(False)
    
    # safe=check_safe_browsing(url)
    
    
    # put information in mongo along with details
    if not inappropriate and not slur:
      return jsonify(True)
    else:
      return jsonify(False)
  
    
    
@filter.route("/blocked", methods=["POST"])
def get_blocked():
    data = request.json
    child=Childrens.objects(_id=ObjectId(data["child"])).first()
    visits=Visits.objects(childrens=ObjectId(data["child"]),isblocked=True)
    return jsonify(visits)
    
    
    
