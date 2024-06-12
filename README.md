# S3 Backup Script

This script compresses a specified directory into a ZIP file and uploads it to an AWS S3 bucket. It is useful for creating backups of local directories and storing them in a secure, scalable storage service provided by AWS.

## Features

- Compresses the contents of a specified directory into a ZIP file.
- Uploads the ZIP file to a specified AWS S3 bucket.
- Deletes the temporary ZIP file after the upload is complete.

## Prerequisites

- Python 3.x
- `boto3` library
- AWS credentials configured in `~/.aws/credentials`

## AWS Configuration

Ensure your AWS credentials are configured correctly in `~/.aws/credentials`. The file should look like this:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

You must also ensure that your AWS IAM user has the necessary permissions to upload files to the specified S3 bucket. 

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-username/s3_backup.git
   cd s3_backup
   ```

2. **Create a virtual environment and activate it(optional):**

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**

   ```sh
   pip install boto3
   ```

## Usage

Run the script with the following command:

```sh
python s3_sync.py /path/to/directory --bucket your-s3-bucket-name
```

### Example

```sh
python s3_sync.py /home/user/documents --bucket my-backups-andrey
```

## Running with Cron

To automate the backup process, you can set up a cron job. Open your crontab file:

```sh
crontab -e
```

Add the following line to schedule the script to run daily at midnight:

```sh
0 0 * * * /path/to/your/venv/bin/python /path/to/your/s3_sync.py /path/to/directory --bucket your-s3-bucket-name
```

Replace `/path/to/your/venv/bin/python` with the path to your Python interpreter in the virtual environment and update the script and directory paths as needed.

## Script Explanation

### Imports

```python
import logging
import os
from zipfile import ZipFile
import boto3
import datetime
import argparse
```

- **logging**: Used for logging information and errors.
- **os**: Provides functions for interacting with the operating system.
- **zipfile**: Used to create and manipulate ZIP files.
- **boto3**: AWS SDK for Python, used to interact with S3.
- **datetime**: Used to handle dates and times.
- **argparse**: Used to parse command-line arguments.

### Configuration

```python
logging.basicConfig(level=logging.INFO)
s3_client = boto3.client("s3")
```

- Sets up logging to display INFO level messages.
- Initializes an S3 client using `boto3`.

### Functions

- **compress_file(dir_path, out_name)**: Compresses the specified directory into a ZIP file.

  ```python
  def compress_file(dir_path, out_name) -> str:
      try:
          with ZipFile(out_name, "w") as zipf:
              for root, dirs, files in os.walk(dir_path):
                  for file in files:
                      zipf.write(os.path.join(root, file))
          logging.info(f"Directory {dir_path} compressed to {out_name}")
          return out_name
      except Exception as e:
          logging.error(f"Exception {e}")
          return None
  ```

- **upload_to_s3(file_name, bucket_name, s3_client)**: Uploads the specified file to the given S3 bucket.

  ```python
  def upload_to_s3(file_name, bucket_name, s3_client) -> bool:
      try:
          s3_client.upload_file(file_name, bucket_name, file_name)
          logging.info(f"File {file_name} uploaded to S3 bucket {bucket_name}")
          return True
      except Exception as e:
          logging.error(f"Exception {e}")
          return False
  ```

### Main Function

- **main(dir_path: str, bucket_name: str)**: Orchestrates the compression and upload process.

  ```python
  def main(dir_path: str, bucket_name: str) -> None:
      current_time = datetime.datetime.now()
      time_str = current_time.strftime("%Y-%m-%d")
      out_name = f"archive_{time_str}.zip"

      compressed_file = compress_file(dir_path, out_name)
      if compressed_file:
          success = upload_to_s3(compressed_file, bucket_name, s3_client)
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
  ```

### Command-Line Arguments

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync the directory to S3")
    parser.add_argument("dir_path", help="Path to the directory to compress and upload")
    parser.add_argument("--bucket", required=True, help="Name of the S3 bucket")
    args = parser.parse_args()
    main(args.dir_path, args.bucket)
```

- Parses command-line arguments to get the directory path and S3 bucket name.
- Calls the `main` function with the parsed arguments.

---# S3-Backup-Script
