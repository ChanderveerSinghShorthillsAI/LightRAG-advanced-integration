import boto3
import traceback
from botocore.exceptions import ClientError
# from app.utils.logger import logger
from app.core.settings import settings


class AWSBase:
    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
        service_name: str | None = None,
    ):
        self.aws_access_key_id = aws_access_key_id or settings.aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key or settings.aws_secret_access_key
        self.region_name = region_name or settings.aws_region
        self.service_name = service_name

        if not self.service_name:
            raise ValueError("Service name is required")

        if (
            not self.aws_access_key_id
            or not self.aws_secret_access_key
            or not self.region_name
        ):
            raise ValueError("AWS credentials and region are not provided/not set in environment variables.")
        try:
            self.client = self.get_client()
        except ClientError as e:
            # logger.error(f"Error in creating client: {e}\n{traceback.format_exc()}")
            pass

    def get_client(self):
        return boto3.client(
            service_name=self.service_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )