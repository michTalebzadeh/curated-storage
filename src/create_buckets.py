from __future__ import print_function
import sys
sys.path.append('/home/hduser/dba/bin/python/curated_storage/')
sys.path.append('/home/hduser/dba/bin/python/curated_storage/conf')
sys.path.append('/home/hduser/dba/bin/python/curated_storage/src')

from conf import variables as v

import datetime
from google.cloud import storage
from os import listdir
from os.path import isfile, join
import time

def main():
    buckets = Buckets()
    bucket = buckets.createBucket()
    buckets.create_table_folder(bucket)
    buckets.create_date_folder(bucket)
    buckets.create_folders(bucket)

class Buckets:
    def createBucket(self):
        client = storage.Client()
        bucket = storage.Bucket(client, v.bucket_name)
        if(bucket.exists()):
          print(f""" bucket {bucket} alredy exists""")
        else:
          print(f"""\n creating bucket {v.bucket_name} in location {v.bucket_location}\n""")
          bucket.create(location=v.bucket_location)
          bucket = storage.Bucket(client, v.bucket_name)
        return bucket

    def create_table_folder(self,bucket):
      #Upload a dummy file to GCP bucket to work around creating folders in Cloud storage!
      files = [f for f in listdir(v.localFolder) if isfile(join(v.localFolder, f))]
      for file in files:
        localFile = v.localFolder + file
        blob = bucket.blob(v.table_name + '/' + file)
        #print(blob)
        blob.upload_from_filename(localFile)
 
    def create_date_folder(self,bucket):
      #Upload a dummy file to GCP bucket to work around creating folders in Cloud storage!
      files = [f for f in listdir(v.localFolder) if isfile(join(v.localFolder, f))]
      for file in files:
        localFile = v.localFolder + file
        blob = bucket.blob(v.table_name + '/created='+v.created + '/' + file)
        #print(blob)
        blob.upload_from_filename(localFile)

    def create_folders(self,bucket):
      files = [f for f in listdir(v.localFolder) if isfile(join(v.localFolder, f))]
      for file in files:
        localFile = v.localFolder + file
        for month in v.dates:
          for region in v.regions:
            blob = bucket.blob(v.table_name + '/created='+v.created + '/date1='+month + '/regionname1='+region + '/entity_id='+v.table_name + '/' +file)
            print(blob) 
            time.sleep(5)
            blob.upload_from_filename(localFile)
            
if __name__ == "__main__":
  main()
