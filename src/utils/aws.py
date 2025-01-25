import boto3
import uuid

def getS3uri(event: dict):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    s3_filepath = f"s3://{bucket_name}/{file_key}"
    
    return s3_filepath

def rename_s3_object(s3_filepath: str):
    if not s3_filepath.startswith("s3://"):
        raise ValueError("Invalid S3 URI format. It should start with 's3://'.")
    _, bucket_name, *key_parts = s3_filepath.split("/")
    file_key = "/".join(key_parts)
    
    s3 = boto3.resource('s3')
    
    ext = file_key.split(".")[-1] if "." in file_key else ""
    new_name = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    
    copy_source = {'Bucket': bucket_name, 'Key': file_key}
    new_key = f"{'/'.join(key_parts[:-1])}/{new_name}" if "/" in file_key else new_name
    
    s3.Object(bucket_name, new_key).copy_from(CopySource=copy_source)
    
    s3.Object(bucket_name, file_key).delete()
    
    return f"s3://{bucket_name}/{new_key}"
