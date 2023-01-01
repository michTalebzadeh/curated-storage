# GCP Cloud storage variable
appName = "create_buckets"
bucket_name = "curated_storage_tests2"
table_name = "kcwhouseprices_2018"
bucket_location = "us"
localFolder = "/home/hduser/dummyfiles/"
dates = ['2018-01-01','2018-02-01','2018-03-01','2018-04-01','2018-05-01','2018-06-01','2018-07-01','2018-08-01','2018-09-01','2018-10-01','2018-11-01','2018-12-01']
regions = ['Kensington and Chelsea','City of Westminster']
created = "20221230"

# GCP variables
projectname = 'GCP First Project'
bucketname = 'etcbucket'
dataset = 'staging'
bqTable = 'KCWHouseprices_2018' 
bqtempTable = 'kCWHouseprices_2018_temp' 
bqExternalTable = 'KCWHouseprices_2018_EXT2' 
bqFields = 99
bqRows = 1000 

# GCP table schema
	
col_names = ['date', 'regionname', 'salesvolume','date1', 'regionname1', 'entity_id']
col_types = ['DATE', 'STRING', 'INTEGER', 'DATE', 'STRING', 'STRING']
col_modes = ['NULLABLE', 'NULLABLE', 'NULLABLE', 'NULLABLE', 'NULLABLE', 'NULLABLE']
