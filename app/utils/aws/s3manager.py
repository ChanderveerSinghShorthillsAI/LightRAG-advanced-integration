from .aws import AWSBase
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import os
# from app.utils.logger import logger

load_dotenv()


class S3Manager(AWSBase):
    def __init__(self, bucket_name: str = "", *args, **kwargs):
        if not bucket_name:
            raise ValueError("Bucket name must be provided.")
        self.bucket_name = bucket_name
        super().__init__(
            service_name="s3",
            **kwargs,
        )

    def upload_file(self, local_file_path: str, s3_folder: str = "") -> str:
        """
        Upload a file to S3 bucket.
        
        Args:
            local_file_path: Path to the local file to upload
            s3_folder: Optional folder path in S3 bucket
            
        Returns:
            str: S3 key of the uploaded file
        """
        try:
            if not os.path.exists(local_file_path):
                # logger.error(f"File does not exist: {local_file_path}")
                raise FileNotFoundError(f"File does not exist: {local_file_path}")
            
            # Get the file name from the path
            file_name = os.path.basename(local_file_path)
            
            # Create the S3 key (path in bucket)
            s3_key = f"{s3_folder}/{file_name}" if s3_folder else file_name
            
            # Upload the file
            self.client.upload_file(local_file_path, self.bucket_name, s3_key)
            
            # logger.info(f"Successfully uploaded file to S3: {s3_key}")
            return s3_key
            
        except ClientError as e:
            # logger.error(f"Error uploading file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            # logger.error(f"Unexpected error uploading file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")


    def get_object(self, object_key):
        """Retrieve an object from S3 bucket"""
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
            return response["Body"].read()
            # return response["Body"].read().decode("utf-8")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                print(f"The object {object_key} does not exist.")
                raise Exception(f"The object {object_key} does not exist.")
            else:
                print(f"Error: {e}")
                raise Exception(f"Error: {e}")
        except Exception as e:
            raise Exception(f"{e}")

    def get_objects(self, object_keys):
        """Retrieve multiple objects from S3 bucket"""
        try:
            objects = list()
            for object_key in object_keys:
                response = self.client.get_object(
                    Bucket=self.bucket_name, Key=object_key
                )
                content = response["Body"].read()
                objects.append(content)
            return objects
        except ClientError as e:
            print(f"Error: {e}")
            raise Exception(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")

    def download_object(self, object_key, local_file_path):
        """Download an object from S3 bucket"""
        try:
            self.client.download_file(self.bucket_name, object_key, local_file_path)
        except ClientError as e:
            print(f"Error: {e}")
            raise Exception("Failed to download file")
        except NoCredentialsError:
            print("Credentials not available")
            raise Exception("Credentials not available")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(f"Failed to download file: {e}")

    def list_objects(self, prefix: str = "") -> list:
        """List files in an S3 bucket"""
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            items = list()

            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if "Contents" in page:
                    for obj in page["Contents"]:
                        items.append(obj["Key"])

            return items
        
        except ClientError as e:
            print(f"Error: {e}")
            raise Exception("Failed to list files " + self.bucket_name)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise ClientError({"Error": {"Code": e.response["Error"]["Code"], "Message": f"Error moving object: {e.response['Error']['Message']}", }},"CopyObject",)

    async def move_s3_object(self, source_key, destination_key: str):
        """
        Move an object from one folder to another within the same S3 bucket.

        :param bucket: Name of the S3 bucket
        :param source_key: Key (path) of the source object in the bucket
        :param destination_key: Key (path) of the destination object in the bucket
        """
        if not self.bucket_name or not source_key or not destination_key:
            raise ValueError(
                "Bucket name, source key, and destination key must be provided."
            )
        try:
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource={"Bucket": self.bucket_name, "Key": source_key},
                Key=destination_key,
            )
            self.client.delete_object(Bucket=self.bucket_name, Key=source_key)

        except ClientError as e:
            print(f"Error moving object: {e}")
            raise ClientError(f"Failed to move object for operation {e.operation_name}")

    def check_file(self, object_key):
        """
        Check if files exist in the specified S3 bucket and return their status.

        Args:
        - object_key (str): File name to check in the S3 bucket.
        Returns:
        - bool: True if the file exists, False otherwise.
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False
            elif error_code == "403":
                raise ClientError(f"Access denied for object: {object_key}")
        except Exception as e:
            raise Exception(f"{str(e)}")

    def check_files(self, file_keys):
        """
        Check if files exist in the specified S3 bucket and return their status.

        Args:
        - file_keys (list): List of file names to check in the S3 bucket.

        Returns:
        - dict: Dictionary with file names as keys and existence status (True/False) as values.
        """
        file_status = {}

        for key in file_keys:
            try:
                self.client.head_object(Bucket=self.bucket_name, Key=key)
                file_status[key] = True
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    file_status[key] = False
                    return False
                elif error_code == "403":
                    raise ClientError(f"Access denied for object: {key}")
            except Exception as e:
                print(f"Unexpected error checking {key}: {e}")
                file_status[key] = False
        return file_status

    def put_object(self, object_key, content):
        """Upload an object to S3 bucket"""
        try:
            self.client.put_object(
                Bucket=self.bucket_name, Key=object_key, Body=content
            )

        except ClientError as e:
            print(f"Error: {e}")
            raise Exception("Failed to upload file")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(f"Failed to upload file: {e}")
    
    def get_presigned_urls(self, folder_name, image_file_names, expiration=1800):
        if not folder_name or not isinstance(folder_name, str):
            raise ValueError("folder_name must be a non-empty string.")

        if not folder_name.endswith('/'):
            folder_name += '/'

        presigned_urls = []

        for image_file_name in image_file_names:
            if not isinstance(image_file_name, str) or not image_file_name.strip():
                print(f"Skipping invalid file name: {image_file_name}")
                presigned_urls.append(None)
                continue  

            s3_key = folder_name + image_file_name
            try:
                presigned_url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration  
                )
                presigned_urls.append(presigned_url)
            except Exception as e:
                print(f"Error generating presigned URL for {s3_key}: {e}")
        return presigned_urls