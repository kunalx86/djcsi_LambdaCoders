import requests
from google.cloud import language_v1
import requests
from google.cloud import language_v1
from google.cloud.language_v1 import types

def get_entities(url):
  client = language_v1.LanguageServiceClient()

  # Call the analyze_entities method of the Natural Language API client
  response = client.analyze_entities(
      document=language_v1.Document(
          content=url,
          type_=types.Document.Type.PLAIN_TEXT
      ),
      encoding_type=types.EncodingType.UTF8
  )

  # Print the keywords extracted from the website content
  for entity in response.entities:
    print(entity,' ',language_v1.Entity.Type)
  #     if entity.type == language_v1.Entity.Type.KEYWORD:
  #         print(entity.name)

def analyze_website(url):

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
    print(entities)
    # Check if any of the entities are flagged as sensitive
    sensitive_entities = ["drugs", "alcohol", "gambling", "violence","sex","rape"]
    for entity in entities:
        if entity.lower() in sensitive_entities:
            return True

    # Check if the sentiment score is below a certain threshold
    if sentiment < -0.5:
        return True

    # If no sensitive content is detected, return False
    return False

# Example usage
url = "https://www.example.com"
url = "https://www.reddit.com/r/confessions/comments/12f3a04/i_looked_through_my_husband_porn/"

# contains_inappropriate_content = analyze_website(url)
# print(contains_inappropriate_content)

get_entities(url)
