import pymongo
from pymongo import MongoClient
import ssl
import yaml


class dB:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.read_config()
        self.db = self.get_database()

# Function to read the configuration from the YAML file
    def read_config(self):
        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    # Function to get the database
    def get_database(self):
        try:
            # Create the connection URI
            uri = (
                f"mongodb://{self.config['mongo']['username']}:{self.config['mongo']['password']}@"
                f"{self.config['mongo']['host']}:{self.config['mongo']['port']}/"
                f"?ssl={self.config['mongo']['ssl']}&replicaSet={self.config['mongo']['replicaset']}&retryWrites={self.config['mongo']['retrywrites']}"
                f"&maxIdleTimeMS={self.config['mongo']['maxidletime']}&appName={self.config['mongo']['appname']}"
            )
            print(uri)
            # Connect to the MongoDB client
            client = MongoClient(uri)

            # Access the database
            db = client[self.config["mongo"]["db_name"]]
            print(f"Connected to database: {self.config['mongo']['db_name']}")
            return db
        except Exception as e:
            print(f"Failed to connect to database: {self.config['mongo']['db_name']}")
            print("Error:", str(e))
            return None


    # Function to insert a document into a collection
    def insert_document(self, collection_name, document):
        # if not db and False:
        if False:
            print("DB connection not established ")
        else:
            try:
                collection = self.db[collection_name]
                result = collection.insert_one(document)
                print(f"Document inserted with ID: {result.inserted_id}")
            except Exception as e:
                print("Failed to insert document")
                print("Error:", str(e))


# Example usage
if __name__ == "__main__":
    # Read the configuration from the YAML file
    db = dB(config_path="db_config.yaml")
    # config = read_config("config.yaml")

    if db.db is not None:
        # Example document to insert
        example_document = { "job_id": "",
                     "date_posted": "",
                     "company_name": "",
                     "job_title": "",
                     "job_type": "",
                     "description_summary": "only 30 words" ,
                     "experience": "",
                     "minimum_qualification": "",
                     "qualification": "",
                     "location": "",
                     "country": "",
                     "source_link": "",
                     "apply_link": ""
      }

        # Insert the document into the specified collection
        db.insert_document(collection_name=db.config["mongo"]["collection_name"],
                           document= example_document)
