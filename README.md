Realtime Data Streaming | End-to-End Data Engineering Project


Introduction
This project serves as a comprehensive guide to building an end-to-end data engineering pipeline. It covers each stage from data ingestion to processing and finally to storage, utilizing a robust tech stack that includes Apache Airflow, Python, Apache Kafka, Apache Zookeeper, Apache Spark, and Cassandra. Everything is containerized using Docker for ease of deployment and scalability.


System Architecture

![Data engineering architecture](https://github.com/surajshinde3898/Data-Engineering-Project/assets/63602997/f7f1ecb2-c117-401f-89c5-5fa436e7d739)

The project is designed with the following components:
Data Source: We use randomuser.me API to generate random user data for our pipeline.
Apache Airflow: Responsible for orchestrating the pipeline and storing fetched data in a PostgreSQL database.
Apache Kafka and Zookeeper: Used for streaming data from PostgreSQL to the processing engine.
Control Center and Schema Registry: Helps in monitoring and schema management of our Kafka streams.
Apache Spark: For data processing with its master and worker nodes.
Cassandra: Where the processed data will be stored.

Technologies
Apache Airflow
Python
Apache Kafka
Apache Zookeeper
Apache Spark
Cassandra
PostgreSQL
Docker
Getting Started
Clone the repository:


Run Docker Compose to spin up the services:
docker-compose up
