import logging
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json , col
from pyspark.sql.types import StructType, StructField, StringType


#
def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

    print("keyspace created successfully !!")

def create_table(session , **kwargs):
    session.execute("""
    CREATE TABLE IF NOT EXISTS spark_streams.created_user (
        id UUID PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        postcode TEXT,
        email TEXT,
        username TEXT,
        dob TEXT,
        registered_date TEXT,
        phone TEXT,
        picture TEXT)
    """)

    print("created table successfully !!")


def insert_data(session , **kwargs):
    print("Inserting Data....")

    user_id = kwargs.get("id")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")
    gender = kwargs.get("gender")
    address = kwargs.get("address")
    postcode = kwargs.get("postcode")
    email = kwargs.get("email")
    username = kwargs.get("username")
    dob = kwargs.get("dob")
    registered_date = kwargs.get("registered_date")
    phone = kwargs.get("phone")
    picture = kwargs.get("picture")

    try:
        session.execute("""
            INSERT INTO spark_streams.created_users(user_id, first_name, last_name, gender, address,
             postcode,  email, username , dob , registered_date, phone , picture)
             Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id , first_name , last_name , gender , address , postcode , email , username ,
            dob , registered_date , phone , picture
        ))
        logging.info(f"Data inserted for user_id : {user_id} and username : {username} ")

    except Exception as e:
        logging.error(f'could not insert due to  :{e}')


def connect_to_kafka(spark_conn):
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'localhost:9092') \
            .option('subscribe', 'user_created') \
            .option('startingOffset', 'earliest') \
            .load()

        logging.info("kafka dataframe created successfully !!")
    except Exception as e:
        logging.warning(f"kafka dataframe could not be created because : {e} ")

    return spark_df

def create_spark_connection():
    s_conn = None
    try:
        s_conn = SparkSession.builder \
        .appName("SparkDataStreaming") \
        .config('spark.jars.packages', "com,datastax.spark:spark-cassandra-connector_2.13:3.5.1",
                "org.apache.spark.spark-sql-kafka-0-10_2.13:3.5.1") \
        .config('spark.cassandra.connection.host', 'localhost') \
        .getOrCreate()

        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully !!")

    except Exception as e:
        logging.error(f"Couldn't connect to spark sessions. Exception : {e}")

    return s_conn

def create_cassandra_connection():
    try:
        cluster = Cluster(['localhost'])
        cas_session = cluster.connect()
        return cas_session
    except Exception as e:
        logging.error(f"Couldn't create cassandra connection. Exception : {e}")
        return None

def create_selection_df_from_kafka(spark_df):
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("postcode", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    sel = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select('data.*')
    print(sel)
    return sel

if __name__ == "__main__":
    # created spark connection
    spark_conn = create_spark_connection()

    if spark_conn is not None:
        # connect to kafka with spark connections
        spark_df = connect_to_kafka(spark_conn)
        selection_df = create_selection_df_from_kafka(spark_df)
        session = create_cassandra_connection()

        if session is not None:
            create_keyspace(session)
            create_table(session)
            #insert_data()

            streaming_query = (selection_df.writeStream.format("org.apache.spark.sql.cassandra")
            .option('checkpointLocation', '/tmp/checkpoint')
            .option('keyspace','spark_streams')
            .option('table', 'created_users')
            .start())

            streaming_query.awaitTermination()


