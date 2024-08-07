import boto3
import argparse
from tqdm import tqdm
import os
from rich_argparse import RichHelpFormatter


def upload_to_s3(bucket, path_local, path_s3):
    # checking that s3 path correct (don't start with /)
    if path_s3.startswith("/"):
        path_s3 = path_s3[1:]
    session = boto3.session.Session()
    s3_client = session.client(
        service_name="s3",
        endpoint_url="https://obs.ru-moscow-1.hc.sbercloud.ru",
        region_name="ru-1a",
    )
    # Get the size of the file
    file_size = os.path.getsize(
        path_local
    )  # Callback function to update the tqdm progress bar

    def tqdm_callback(bytes_transferred):
        progress_bar.update(bytes_transferred)

    with tqdm(
        total=file_size, unit="B", unit_scale=True, desc="Uploading"
    ) as progress_bar:
        s3_client.upload_file(
            Filename=path_local,
            Bucket=bucket,
            Key=path_s3,
            ExtraArgs={"ACL": "authenticated-read"},
            Callback=tqdm_callback,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Upload the zip dataset to S3", formatter_class=RichHelpFormatter
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="The name of the S3 bucket",
        default="amr-usr-manip",
    )
    parser.add_argument(
        "--path_local", required=True, help="Path to the file to be uploaded"
    )
    parser.add_argument("--path_s3", required=True, help="S3 key path for the file")
    args = parser.parse_args()

    upload_to_s3(args.bucket, args.path_local, args.path_s3)
    print("Done")


if __name__ == "__main__":
    main()
