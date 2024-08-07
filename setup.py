from setuptools import setup, find_packages

setup(
    name="dataloader",
    version="0.1",
    packages=find_packages(),
    install_requires=["boto3", "tqdm", "Click"],
    entry_points="""
        [console_scripts]
        upload-umi-videos=upload_raw_umi_videos_to_s3:main
    """,
)
