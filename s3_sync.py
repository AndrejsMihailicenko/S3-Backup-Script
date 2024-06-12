'''Script must be run as python s3_sync.py /path/to/directory --bucket bucket-name'''
'''Don't forget to configure your AWS access keys in the ~/.aws/credentials file'''

import logging
import os
from zipfile import ZipFile
import boto3
import datetime
import argparse

logging.basicConfig(level=logging.INFO)
s3_client = boto3.client("s3")  # boto3 imports keys from ~/.aws/credentials 


def compress_file(dir_path, out_name) -> str:
    """Compress the files and return the name of the compressed file"""
    try:
        with ZipFile(out_name, "w") as zipf:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    zipf.write(os.path.join(root, file))  # Write the file to the zip
        logging.info(f"Directory {dir_path} compressed to {out_name}")
        return out_name
    except Exception as e:
        logging.error(f"Exception {e}")
        return None


def upload_to_s3(file_name, bucket_name, s3_client) -> bool:
    """Upload the file to S3"""
    try:
        s3_client.upload_file(file_name, bucket_name, file_name)
        logging.info(f"File {file_name} uploaded to S3 bucket {bucket_name}")
        return True
    except Exception as e:
        logging.error(f"Exception {e}")
        return False


def main(dir_path: str, bucket_name: str) -> None:
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y-%m-%d")
    out_name = f"archive_{time_str}.zip"

    compressed_file = compress_file(dir_path, out_name)  # Compress the directory
    if compressed_file:
        success = upload_to_s3(compressed_file, bucket_name, s3_client)  # Upload the compressed file to S3
        if success:
            logging.info("Backup process completed successfully.")
        else:
            logging.error("Failed to upload the file to S3.")
        try:
            os.remove(compressed_file)
            logging.info(f"Temporary file {compressed_file} removed.")
        except Exception as e:
            logging.error(f"Error removing temporary file: {e}")
    else:
        logging.error("Error in compressing the file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync the directory to S3") # parser for command line arguments
    parser.add_argument("dir_path", help="Path to the directory to compress and upload") # path to the directory
    parser.add_argument("--bucket", required=True, help="Name of the S3 bucket") # name of the S3 bucket
    args = parser.parse_args() # parse the arguments
    main(args.dir_path, args.bucket) # call the main function with the directory path and bucket name
