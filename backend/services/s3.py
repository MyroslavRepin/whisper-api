from backend.config import settings, get_s3_client

s3 = get_s3_client()

def upload_file_to_s3(file_path, bucket_name, object_name):
    s3.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=object_name
    )

