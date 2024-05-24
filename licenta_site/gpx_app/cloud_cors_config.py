from google.cloud import storage
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_directory, '..', 'ServiceKeyGoogleCloud.json')

os.environ['GOOGLE_APPLICATION_CREDENTIALS']=service_account_path


def cors_configuration(bucket_name):
    """Set a bucket's CORS policies configuration."""

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    bucket.cors = [
        {
            "origin": ["http://localhost:5173", "http://127.0.0.1:8000"],
            "responseHeader" : ["*"],           
            "method": ['PUT', 'POST','OPTIONS','GET'],
            "maxAgeSeconds": 3600,
            "credentials" : True
        }
    ]
    bucket.patch()

    print(f"Set CORS policies for bucket {bucket.name} is {bucket.cors}")
    return bucket


def bucket_metadata(bucket_name):
    """Prints out a bucket's metadata."""

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    print(f"ID: {bucket.id}")
    print(f"Name: {bucket.name}")
    print(f"Storage Class: {bucket.storage_class}")
    print(f"Location: {bucket.location}")
    print(f"Location Type: {bucket.location_type}")
    print(f"Cors: {bucket.cors}")
    print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
    print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
    print(f"Metageneration: {bucket.metageneration}")
    print(
        f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
    )
    print(f"Retention Effective Time: {bucket.retention_policy_effective_time}")
    print(f"Retention Period: {bucket.retention_period}")
    print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
    print(f"Object Retention Mode: {bucket.object_retention_mode}")
    print(f"Requester Pays: {bucket.requester_pays}")
    print(f"Self Link: {bucket.self_link}")
    print(f"Time Created: {bucket.time_created}")
    print(f"Versioning Enabled: {bucket.versioning_enabled}")
    print(f"Labels: {bucket.labels}")

def create_bucket(bucket_name):
    """Creates a new bucket."""

    storage_client = storage.Client()

    bucket = storage_client.create_bucket(bucket_name)

    print(f"Bucket {bucket.name} created")   

bucket_name="bucket-licenta-rovin"
cors_configuration(bucket_name)
bucket_metadata(bucket_name)
# create_bucket(bucket_name)
