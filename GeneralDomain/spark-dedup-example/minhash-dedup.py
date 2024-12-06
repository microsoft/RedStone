'''
Input is a flatted of LSH values for rows. (similar to the output after `posexplode`)
'''

def main(spark):
    from operator import add
    # get lsh cnt per id
    df0 = spark.read.parquet('abfs://container@storage/folder/example.pq')
    first_id = df0.first()['id']
    lsh_cnt = df0.where(df0.id == first_id).count()
    print('lsh count:', lsh_cnt, flush=True)
    # dedup
    df = spark.read.parquet('abfs://container@storage/folder/*.pq')
    rdd = df.rdd.map(lambda x: ((bytes(x['lsh']), x['lsh_pos']), x['id']))
    rdd = rdd.reduceByKey(min)
    rdd = rdd.map(lambda x: (x[1], 1))
    rdd = rdd.reduceByKey(add).filter(lambda x: x[1] == lsh_cnt)
    # output
    df.write.mode('overwrite').parquet('abfs://container@storage/output_folder')

if __name__ == '__main__':
    from pyspark.sql import SparkSession
    spark_config = {
        'spark.jars.packages': 'org.apache.hadoop:hadoop-azure:3.3.4',
    }
    spark = SparkSession.builder.master(
        'spark://127.0.0.1:7077'
    ).config(
        map=spark_config
    ).appName("minhash-dedup").getOrCreate()
    main(spark)
    spark.stop()
