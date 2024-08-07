import os
import shutil
import zipfile
import boto3
from datetime import datetime
from upload_file_to_s3 import upload_to_s3
import tqdm
import click
import argparse


def pack_and_upload(folder_path, task_description, is_bimanual):

    if folder_path is None:
        # Getting path from media
        username = os.getlogin()
        device = os.listdir(f"/media/{username}")[0]
        folder_path = os.path.join(f"/media/{username}", device, "DCIM", "100GOPRO")

    # Get current date
    current_date = datetime.now().strftime("%d.%m.%Y")

    # Create the new folder name
    folder_name = f"{task_description}.{current_date}"

    # Create the new folder
    new_folder_path = os.path.join(os.path.expanduser("~"), "umi_raw_data", folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # Move files to the new folder
    raw_videos_folder = os.path.join(new_folder_path, "raw_videos")
    os.makedirs(
        raw_videos_folder, exist_ok=False
    )  # Ensure the directory exists or create it

    files = [
        file
        for file in os.listdir(folder_path)
        if file.endswith(".MP4") or file.endswith(".mp4")
    ]
    for file in tqdm.tqdm(files, desc="Moving files to local storage"):
        shutil.move(os.path.join(folder_path, file), raw_videos_folder)

    # Calculate amount of episodes
    amount_of_episodes = len(os.listdir(raw_videos_folder)) - 2

    assert amount_of_episodes > 0

    # Zip the folder
    zip_file_name = f"{folder_name}.{amount_of_episodes}_episodes.zip"
    zip_file_path = os.path.join(new_folder_path, zip_file_name)
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for root, dirs, files in os.walk(new_folder_path):
            if len(files) > 2:
                for file in tqdm.tqdm(files, desc="Zipping videos"):
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), new_folder_path),
                    )
            else:
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), new_folder_path),
                    )

    # Upload zip file to S3

    s3_zip_path = f"datasets/umi/raw_data/{'bimanual' if is_bimanual else 'single_arm'}/{zip_file_name}"
    upload_to_s3("umi_external", zip_file_path, s3_zip_path)

    print(
        f"Folder packed and uploaded successfully as {zip_file_name} to S3: {s3_zip_path}"
    )
    print(f"Cleaning SD card...{folder_name}")
    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))


def main():
    parser = argparse.ArgumentParser(
        description="Upload raw UMI videos to S3 and cleaning SD card"
    )

    parser.add_argument(
        "--sd_card_path",
        required=False,
        default=None,
        help="Path to the SD card storage",
    )
    parser.add_argument(
        "--bimanual", required=False, type=bool, help="Is bimanual manipulation or not"
    )

    args = parser.parse_args()
    task_description = input("Enter the task description: ").lower().replace(" ", "_")
    pack_and_upload(args.sd_card_path, task_description, args.bimanual)


if __name__ == "__main__":
    main()
