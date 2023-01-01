from __future__ import print_function
import sys
sys.path.append('/home/hduser/dba/bin/python/curated_storage/')
sys.path.append('/home/hduser/dba/bin/python/curated_storage/conf')
sys.path.append('/home/hduser/dba/bin/python/curated_storage/src')
from os import listdir
from os.path import isfile, join
import time

from conf import variables as v

# google stuff
from google.cloud import storage
from google.cloud import bigquery
import google.auth
from google.cloud.exceptions import NotFound
from google import resumable_media
import pandas as pd

def main():
  tables = Tables()
  #tables.drop_if_bqtempTable_exists()
  #tables.bq_create_bqtempTable()
  #tables.bq_populate_tempTable()
  #tables.remove_dummy_files()
  tables.bq_create_external_table()
  
class Tables:
  
  def drop_if_bqtempTable_exists(self):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(v.dataset)
    table_ref = dataset_ref.table(v.bqtempTable)
    try:
      bigquery_client.get_table(table_ref)
    except NotFound:
      print('table ' + v.bqtempTable + ' does not exist')
      return False
    try:
      print('table ' + v.bqtempTable + ' exists, dropping it')
      bigquery_client.delete_table(table_ref) 
      return True
    except:
      print('Error deleting table ' + v.bqtempTable)
      sys.exit(1)

  def bq_create_bqtempTable(self):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(v.dataset)
    table_ref = dataset_ref.table(v.bqtempTable)
    schema = [
        bigquery.SchemaField(v.col_names[0], v.col_types[0], v.col_modes[0])
      , bigquery.SchemaField(v.col_names[1], v.col_types[1], v.col_modes[1])
      , bigquery.SchemaField(v.col_names[2], v.col_types[2], v.col_modes[2])
    ]
    table = bigquery.Table(table_ref, schema=schema)
    table = bigquery_client.create_table(table)
    print(f"""Table {v.bqtempTable} created.""")

  def bq_populate_tempTable(self):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(v.dataset)
    table_ref = dataset_ref.table(v.bqtempTable)
    for month in v.dates:
      for region in v.regions:
        # populate temp table to export to GCS relevant bucket
        sqltext = f"""
          DELETE FROM {v.dataset}.{v.bqtempTable} WHERE 1 = 1; 
          INSERT INTO {v.dataset}.{v.bqtempTable}
          SELECT 
              date
            , regionname
            , salesvolume
          FROM {v.dataset}.{v.bqTable}
          WHERE
          date = '{month}'
          AND
          regionname = '{region}';
        """
        #print(sqltext)
        query_job = bigquery_client.query(sqltext)
        results = query_job.result()
        # Now export to GCS folders
        destination_uri="gs://"+v.bucket_name+"/"+v.table_name+"/created="+v.created+"/date1="+month+"/regionname1="+region+"/entity_id="+v.table_name+"/*"
        #print(destination_uri)
        job_config = bigquery.ExtractJobConfig()
        job_config.compression = bigquery.Compression.GZIP
        job_config.destination_format = "PARQUET"
        extract_job = bigquery_client.extract_table(
          table_ref,
          destination_uri,
          location = v.bucket_location,
          job_config = job_config
        )
        extract_job.result()    

  def remove_dummy_files(self):
    # https://www.skytowner.com/explore/removing_files_on_google_cloud_storage_using_python
    client = storage.Client()
    bucket = storage.Bucket(client, v.bucket_name)
    files = [f for f in listdir(v.localFolder) if isfile(join(v.localFolder, f))]
    for file in files:
        localFile = v.localFolder + file
        try:
          blob = bucket.blob(v.table_name + '/' + file)
          print(f"""deleting blob {blob}""")
          blob.delete()
        except NotFound:
          print(f"""blob {blob} does not exist""")
        try:
          blob = bucket.blob(v.table_name + '/created='+v.created +'/' + file)
          print(f"""deleting blob {blob}""")
          blob.delete()
        except NotFound:
          print(f"""blob {blob} does not exist""")

        for month in v.dates:
          for region in v.regions:
            try:
              blob = bucket.blob(v.table_name + '/created='+v.created + '/date1='+month + '/regionname1='+region + '/entity_id='+v.table_name + '/' +file)
              print(f"""deleting blob {blob}""")
              #time.sleep(5)
              blob.delete()
            except NotFound:
              print(f"""blob {blob} does not exist""")
  
  def bq_create_external_table(self):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(v.dataset)
    table_ref = dataset_ref.table(v.bqExternalTable)
    schema = [
        bigquery.SchemaField(v.col_names[0], v.col_types[0], v.col_modes[0])
      , bigquery.SchemaField(v.col_names[1], v.col_types[1], v.col_modes[1])
      , bigquery.SchemaField(v.col_names[2], v.col_types[2], v.col_modes[2])
      , bigquery.SchemaField(v.col_names[3], v.col_types[3], v.col_modes[3])
      , bigquery.SchemaField(v.col_names[4], v.col_types[4], v.col_modes[4])
      , bigquery.SchemaField(v.col_names[5], v.col_types[5], v.col_modes[5])
     ]
    external_table_options = {
      "autodetect": True,
      "maxBadRecords": 9999999,
      "sourceFormat": "PARQUET",
      "sourceUris": "gs://"+v.bucket_name+"/"+v.table_name+"/created="+v.created+"/*"
    }
    external_config = bigquery.ExternalConfig.from_api_repr(external_table_options)
    table = bigquery.Table(table_ref, schema=schema)
    table.external_data_configuration = external_config
    bigquery_client.create_table(table)
    #destination_table = bigquery_client.get_table(table_ref)
    print('table {} created.'.format(table.table_id))
    sqltext = """
    SELECT
       n.date
     , n.regionname
     --, e.date
     --, e.regionname
     , n.salesvolume -e.salesvolume AS diff
    FROM
      `axial-glow-224522.staging.KCWHouseprices_2018` n
     ,`axial-glow-224522.staging.kCWHouseprices_2018_EXT` e
    WHERE
      n.date = e.date
    AND 
      n.regionname = e.regionname
    ORDER BY
      1, 2;
    """
    query_job = bigquery_client.query(sqltext)
    data = query_job.result()
    rows = list(data)
    df = pd.DataFrame(rows)
    print(df.head(10))

if __name__ == "__main__":
  main()
