import boto3
import io
from botocore.exceptions import ClientError
from tensorflow.keras.models import load_model
import h5py
from io import BytesIO
import os

class AWSUtils:
    bucket_name = os.getenv('AWS_BUCKET_NAME_RHD')
    print(bucket_name)
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

    @classmethod
    def load_model_from_s3(cls, s3_key):
        """
        Load a model file directly from S3 into memory using Keras.
        
        :param s3_key: The key of the model file in the S3 bucket.
        :return: The loaded Keras model.
        """
        try:
            # Stream the S3 object into memory
            obj = cls.s3.get_object(Bucket=cls.bucket_name, Key=s3_key)
            bytestream = io.BytesIO(obj['Body'].read())

            # Load the model from the bytestream
            return load_model(h5py.File(bytestream, 'r'))
        except Exception as e:
            print(f"Error loading model from S3: {e}")
            return None

    @classmethod   
    def load_file_from_s3(cls, s3_key):
        """
        Loads a file from AWS S3 bucket.

        Parameters:
        - s3_key: The key (path + filename) of the file in the S3 bucket.

        Returns:
        - A file-like object containing the contents of the file.
        - None if the file doesn't exist or there was an error.
        """
        try:
            obj = cls.s3.get_object(Bucket=cls.bucket_name, Key=s3_key)
            return BytesIO(obj['Body'].read())
        except ClientError as e:
            print(f"Error loading file from S3: {e}")
            return None
        
    @classmethod
    def upload_file_to_s3(cls, file_obj, s3_key):
        """
        Uploads a file object to AWS S3 bucket.

        Parameters:
        - file_obj: File-like object (e.g., from request.files['file'])
        - s3_key: S3 object key (path + filename) to upload the file

        Returns:
        - True if successful, False otherwise
        """
        try:
            # Upload file object to S3 bucket
            cls.s3.upload_fileobj(file_obj, cls.bucket_name, s3_key)
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False