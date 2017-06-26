from s3utils import download_data_from_s3
from config import CURRENT_DATA_FILENAME

if __name__ == "__main__":
    download_data_from_s3(CURRENT_DATA_FILENAME, bucket_name="scarp-data")
