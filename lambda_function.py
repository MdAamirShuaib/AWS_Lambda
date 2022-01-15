import json
import os
import sys
import time
import requests
from transcribe import *
from assemblyai_data_extraction import json_data_extraction
import boto3


def lambda_handler(event, context):
    
    access_key1 = os.environ.get('access_key')
    secret_key1 = os.environ.get('secret_key')

    s3_resource = boto3.resource(service_name= "s3", region_name="us-east-1", aws_access_key_id= access_key1, aws_secret_access_key= secret_key1)

    print("Collecting File Names")

    video_items = []
    for obj in s3_resource.Bucket("upload-video-transcription-osg").objects.filter(Prefix="video_files_to_transcribe/"):
        video_items.append(obj.key.replace("video_files_to_transcribe/",""))

    fname = video_items[1]

    print("Downloading Files")
    
    s3_resource.Bucket("upload-video-transcription-osg").download_file(Key="video_files_to_transcribe/"+fname, Filename="/tmp/"+fname)
    
        
    filepath = "/tmp/"+fname

    token = "10c3286baa1e4429b0095eabd6480582"
    
    print("Uploading file to AssemblyAI")

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
    df.to_csv("/tmp/"+fname+".csv")

    # output_path = 'C:\\Users\\Shubham Verma\\Project\\ConversationalAnalytics\\Julie\\transcripts'
    # df.to_csv(output_path+'\\'+fname+'.csv',index=False)
    print("Uploading file to S3 Bucket")
    
    # Upload files to s3
    s3_resource.Bucket("upload-video-transcription-osg").upload_file(Filename="/tmp/"+fname+".csv", Key="Transcribed_documents/"+fname+".csv")

    print("Deleting Downloaded Files from Directory")

    os.remove("/tmp/"+fname)
    os.remove("/tmp/"+fname+".csv")

    print("Hurray completed!!!")