import os
import time
import boto3
import mimetypes
from dotenv import load_dotenv

load_dotenv()

def invalidate_cloudfront():
    """Creates an invalidation in CloudFront to clear the cache instantly."""
    dist_id = os.getenv('CLOUDFRONT_DIST_ID')
    if not dist_id:
        print("⚠️ Notice: CLOUDFRONT_DIST_ID not set in .env. Skipping cache invalidation.")
        return

    print("🔄 Clearing CloudFront cache so updates appear instantly for players...")
    try:
        cf_client = boto3.client(
            'cloudfront',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # CloudFront requires a unique caller reference for every invalidation request
        unique_reference = str(time.time())
        
        response = cf_client.create_invalidation(
            DistributionId=dist_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': unique_reference
            }
        )
        print("✅ CloudFront cache successfully cleared!")
    except Exception as e:
        print(f"❌ Failed to clear CloudFront cache: {e}")

def deploy_to_s3(tournament_name):
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("❌ Error: S3_BUCKET_NAME not found in .env file.")
        return

    print(f"\n🚀 Connecting to AWS S3 bucket: {bucket_name}...")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    safe_name = tournament_name.replace(" ", "_").lower()
    output_dir = os.path.join('output', safe_name)
    
    if not os.path.exists(output_dir):
        print(f"❌ Error: {output_dir} directory does not exist. Build the site first.")
        return

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        
        if os.path.isfile(filepath):
            content_type, _ = mimetypes.guess_type(filepath)
            content_type = content_type or 'application/octet-stream'
            
            s3_key = f"{safe_name}/{filename}"
            
            try:
                print(f"Uploading {filename} to /{s3_key}...")
                s3_client.upload_file(
                    filepath, 
                    bucket_name, 
                    s3_key,
                    ExtraArgs={'ContentType': content_type}
                )
            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")
                
    print(f"✅ S3 Deployment complete for {tournament_name}!")
    
    # Trigger the cache clear immediately after uploading
    invalidate_cloudfront()

def deploy_master_portal():
    """Pushes the root index.html to the base of the S3 Bucket."""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name: return
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    filepath = os.path.join('output', 'index.html')
    if os.path.exists(filepath):
        try:
            print("🚀 Uploading Master Portal to root URL...")
            s3_client.upload_file(
                filepath, 
                bucket_name, 
                'index.html',
                ExtraArgs={'ContentType': 'text/html'}
            )
            print("✅ Master Portal uploaded to S3!")
            
            # Trigger the cache clear immediately after uploading
            invalidate_cloudfront()
        except Exception as e:
            print(f"❌ Failed to upload Master Portal: {e}")