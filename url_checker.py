from bs4 import BeautifulSoup 
import nltk
import requests
import random
import boto3
import os
from botocore.client import Config
#from nltk.stem import PorterStemmer
# from nltk import word_tokenize
# import re, string, unicodedata
#from nltk import StandfordNERTagger
# from nltk.corpus import stopwords
#import contractions
#import inflect
from googleapiclient.discovery import build

my_api_key = "AIzaSyALuVy4y4s_NnbKZMLMxsDADUzzc68uRj0"
my_cse_id = "005571930952353776901:dg4xam6kxv8"
conference_urls = []
ACCESS_KEY_ID = 'AKIAJOKGYZOOSORXGRDA'
ACCESS_SECRET_KEY = '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'
BUCKET = 'image-urls-1'
seq = range(1,100)


def google_search(search_term, api_key, cse_id, **kwargs):
      service = build("customsearch", "v1", developerKey=my_api_key)
      res = service.cse().list(q=search_term, cx=my_cse_id,**kwargs).execute()
      return res['items']
results = google_search("conference on blockchain",my_api_key,my_cse_id,num=10) 
def get_link(results):
      for result in results:
            link = result['formattedUrl']
            if 'http' in link:
                  link = link
            else:
                  link = ("http://" + link)
            if "blog" in link or 'wiki' in link or '...' in link or 'quora' in link or 'youtube' in link or 'hackernoon' in link:
                  yup = link
                  print(yup)
                  print("This is not a conference link")
            else:
                  print(link)
                  #count1 = 0
                  #count2 = 0
                  def image_link(link):
                        imgs_urls = []
                        source = requests.get(link).text
                        soup = BeautifulSoup(source,'html.parser')
                        img_tags = soup.find_all('img')
                        for img in img_tags:
                              image = str(img)
                              if 'src' in image:
                                    img['src'] = (image.split('src="')[1].split('"')[0])
                                    if 'http' not in img['src']:
                                          img['src'] = (link + img['src'])
                                    if 'jpeg' in img['src'] or 'png' in img['src'] or 'jpg' in img['src']:
                                          img['src'] = (img['src'].split('?'))[0]
                                          imgs_urls.append(img['src'])
                                    # print(imgs_urls)
                        return(imgs_urls)
                  imgs_urls = image_link(link)          
                  def get_image(imgs_urls):
                        # count1 = 0
                        # count2 = 0
                        for img in imgs_urls:
                              image_name = str(random.choice(seq)) + '.' + img.split('.')[-1]
                              image = open('./yes2/'+image_name,'wb')
                              image.write(requests.get(img).content)

                              def s3_rekognition(image_name):
                                    data = open('./yes2/'+image_name, 'rb')
                                    s3 = boto3.resource(
                                          's3',
                                          aws_access_key_id=ACCESS_KEY_ID,
                                          aws_secret_access_key=ACCESS_SECRET_KEY,
                                          config=Config(signature_version='s3v4')
                                    )
                                    s3.Bucket(BUCKET).put_object(Key='yes2/'+image_name, Body=data)
                                    KEY = ('yes2/'+image_name)
                                    try:
                                          def detect_labels(bucket, key, max_labels=5, min_confidence=95, region="us-east-1"):
                                                rekognition = boto3.client("rekognition", region)
                                                response = rekognition.detect_labels(
                                                Image={
                                                            "S3Object": {
                                                                  "Bucket": bucket,
                                                                  "Name": key,
                                                            }
                                                },
                                                MaxLabels=max_labels,
                                                MinConfidence=min_confidence,
                                                )
                                                return response['Labels']


                                          for label in detect_labels(BUCKET, KEY):
                                                print ("{Name} - {Confidence}%".format(**label))
                                                count1 = count1 + 1
                                          if 'Human' in "{Name}".format(**label):
                                                count2 = count2 + 1 
                                    except Exception as e:
                                          print("got it :-) ", e)
                                    return KEY
                              KEY = s3_rekognition(image_name)
                        return image_name
                  image_name = get_image(imgs_urls)
                  def con_url(count1,count2):
                        temp = 0
                        print("The total number of label detected of images:",count1)
                        print("the count of human in detec labels of images:",count2)
                        if count1 <1:
                              print("The above link is not a conference link")
                        else:
                              temp = (count2*100)/count1
                              if temp >=50:
                                    print("The above link is a conference link")
                        return
                  temp = con_url(count1,count2)

link = get_link(results)
print('done..')
         

'''text = soup.get_text
      tokens = word_tokenize(text())
      re_punc = re.compile('[%s]' %re.escape(string.punctuation))
      tokens = [re_punc.sub('',w) for w in tokens]
      tokens = [word for word in tokens if word.isalpha()]
      tokens = [w.lower() for w in tokens]
      stop_words = set(stopwords.words('english'))
      tokens = [w for w in tokens if not w in stop_words]
      tokens = [word for word in tokens if len(word) > 5]
      count = 0
            
      freq = nltk.FreqDist(tokens) 
      print(freq.most_common(10))'''
