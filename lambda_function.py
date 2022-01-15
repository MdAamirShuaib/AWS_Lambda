import json
import os
import sys
import time
import requests
from transcribe import *
from assemblyai_data_extraction import json_data_extraction
import boto3

access_key = "AKIA2H25YUUMHYJD2CER"
secret_key = "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"
def lambda_handler(event, context):
    
    s3_resource = boto3.resource(service_name="s3", region_name="us-east-1", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    
    video_items = []
    for obj in s3_resource.Bucket("upload-video-transcription-osg").objects.filter(Prefix="video_files_to_transcribe/"):
        video_items.append(obj.key.replace("video_files_to_transcribe/",""))
        
    fname = video_items[0]
    
    s3_resource.Bucket("upload-video-transcription-osg").download_file(Key="video_files_to_transcribe/"+fname, Filename=fname)
    filepath = "/"+fname
    
    tid = upload_file(token,filepath)
    result = {}
    print('started..')
    while result.get("status") != 'processing':
        print(result.get("status"))
        result = get_text(token, tid)
    
    while result.get("status") != 'completed':
        print(result.get("status"))
        result = get_text(token, tid)

    df = json_data_extraction(result,fname)
    print('saving transcript...')
    df.to_csv("/"+fname+".csv")
    # output_path = 'C:\\Users\\Shubham Verma\\Project\\ConversationalAnalytics\\Julie\\transcripts'
    # df.to_csv(output_path+'\\'+fname+'.csv',index=False)
    print('completed!!')
    
    # Upload files to s3
    s3_resource.Bucket("upload-video-transcription-osg").upload_file(Filename=fname+".csv", Key="Transcribed_documents/"+fname+".csv")