import requests
from google.cloud import vision
from google.cloud.vision_v1 import types
import requests
from bs4 import BeautifulSoup
import urllib


# Set up Google Cloud Vision API client
# AIzaSyCFfJRcNJGgxd543-XPrTfi49nd83JLwT8
#export GOOGLE_APPLICATION_CREDENTIALS='creds.json'

client = vision.ImageAnnotatorClient()

# Define function to check if a website contains inappropriate images or videos
def check_website(url):
    response = requests.get(url)
    content_type = response.headers.get('content-type')
    
    if content_type.startswith('image/'):
        # If the URL points to an image, analyze it using the Google Cloud Vision API
        image_content = response.content
        image = types.Image(content=image_content)
        response = client.safe_search_detection(image=image)
        return response.safe_search_annotation.violence >=2
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
      # print(item)
      print(item['src'].find('http'))
      print(item['src'])
      result=check_website(item['src'])
      
      if result:
        #print(item['src'])
        print('The website contains inappropriate content')
      else:
          print('The website does not contain inappropriate content')
  
# Example usage
url = 'https://bellesa.com'
url = 'https://www.shutterstock.com/search/violent'
url="https://www.shutterstock.com/image-photo/flat-lay-composition-evidences-crime-260nw-1859010208.jpg"
url="https://www.shutterstock.com/image-photo/st-petersburg-russia-february-24-260nw-2130361049.jpg"
url="https://www.reddit.com/r/confessions/comments/12f3a04/i_looked_through_my_husband_porn/"

image_parser(url)

