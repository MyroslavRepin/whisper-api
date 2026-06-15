from loguru import logger

from backend.core.config import get_s3_client


class StorageService:
    def __init__(self):
        self.s3_client = get_s3_client()

    def upload_file(self, file, bucket_name: str, object_name: str):
        try:
            logger.debug(f"Uploading to S3: bucket={bucket_name}, key={object_name}")
            self.s3_client.upload_fileobj(file, bucket_name, object_name)
            logger.debug(f"S3 upload complete: {object_name}")
            return {"bucket": bucket_name, "key": object_name}
        except Exception as e:
            logger.error(f"S3 upload failed for {object_name}: {e}")
            raise

    def download_file(self, bucket_name: str, file_key: str, download_path: str):
        try:
            logger.debug(f"Downloading file from S3: bucket={bucket_name}, key={file_key}")
            self.s3_client.download_file(bucket_name, file_key, download_path)
            logger.debug(f"S3 download complete: {download_path}")
            return download_path
        except Exception as e:
            logger.error(f"S3 download failed for {file_key}: {e}")
            raise
