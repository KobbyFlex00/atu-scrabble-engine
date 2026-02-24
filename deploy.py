import os
import boto3
import mimetypes
from dotenv import load_dotenv

# Load credentials from the .env file
load_dotenv()

def deploy_to_s3():
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not bucket_name:
        print("❌ Error: S3_BUCKET_NAME not found in .env file.")
        return

    print(f"\n🚀 Connecting to AWS S3 bucket: {bucket_name}...")
    
    # Initialize the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    output_dir = 'output'
    
    if not os.path.exists(output_dir):
        print(f"❌ Error: {output_dir} directory does not exist. Build the site first.")
        return

    # Loop through all files in the output directory
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        
        # Skip directories
        if os.path.isfile(filepath):
            # Guess the content type (e.g., text/html for .html files)
            content_type, _ = mimetypes.guess_type(filepath)
            content_type = content_type or 'application/octet-stream'
            
            try:
                print(f"Uploading {filename}...")
                s3_client.upload_file(
                    filepath, 
                    bucket_name, 
                    filename,
                    ExtraArgs={'ContentType': content_type}
                )
            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")
                
    print("✅ Deployment complete! Your tournament pages are live.")