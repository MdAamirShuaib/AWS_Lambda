import os
import requests
import pandas as pd

def check(file):
    temp = pd.read_csv('tx_speaker_db.csv')
    if (file in temp.fname.unique()):
        print('file exists')
    else:
        print('transcribe')


def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

def get_url(token,filepath):
  '''
    Parameter:
      token: The API key
      data : The File Object to upload
    Return Value:
      url  : Url to uploaded file
  '''
  headers = {'authorization': token}
  response = requests.post('https://api.assemblyai.com/v2/upload',
                         headers=headers,
                         data=read_file(filepath))
  url = response.json()["upload_url"]
  print("Uploaded File and got temporary URL to file")
  return url

def get_transcribe_id(token,url):
  '''
    Parameter:
      token: The API key
      url  : Url to uploaded file
    Return Value:
      id   : The transcribe id of the file
  '''
  endpoint = "https://api.assemblyai.com/v2/transcript"
  json = {
    "audio_url": url,"speaker_labels": True,"auto_highlights": True
  }
  headers = {
    "authorization": token,
    "content-type": "application/json"
  }
  response = requests.post(endpoint, json=json, headers=headers)
  id = response.json()['id']
  print("Made request and file is currently queued")
  return id

def upload_file(token,filepath):
  '''
    Parameter: 
      filepath: The File Object to transcribe
    Return Value:
      token  : The API key
      transcribe_id: The ID of the file which is being transcribed
  '''
  
  # token = "398a8ab00a764f0092e93ff6a480a68f"
  file_url = get_url(token,filepath)
  transcribe_id = get_transcribe_id(token,file_url)
  return transcribe_id

def get_text(token,transcribe_id):
  '''
    Parameter: 
      token: The API key
      transcribe_id: The ID of the file which is being 
    Return Value:
      result : The response object
  '''  
  endpoint = f"https://api.assemblyai.com/v2/transcript/{transcribe_id}"
  headers = {
    "authorization": token
  }
  result = requests.get(endpoint, headers=headers).json()
  return result
