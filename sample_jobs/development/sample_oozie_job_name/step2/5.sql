CREATE EXTERNAL TABLE IF NOT EXISTS base.us_daily(
  date int,
  states int,
  positive int,
  negative int,
  pending int,
  hospitalizedcurrently int,
  hospitalizedcumulative int,
  inicucurrently int,
  inicucumulative int,
  onventilatorcurrently int,
  onventilatorcumulative int,
  datechecked string,
  death int,
  hospitalized int,
  totaltestresults int,
  lastmodified string,
  recovered string,
  total int,
  posneg int,
  deathincrease int,
  hospitalizedincrease int,
  negativeincrease int,
  positiveincrease int,
  totaltestresultsincrease int,
  hash string)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  '${code_bucket}/base/us_daily';