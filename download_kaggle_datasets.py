import kaggle
import os

def download_dataset(dataset_name, path):
    print(f"Downloading {dataset_name} to {path}...")
    try:
        kaggle.api.dataset_download_files(dataset_name, path=path, unzip=True)
        print(f"Successfully downloaded and unzipped {dataset_name}.")
    except Exception as e:
        print(f"Error downloading {dataset_name}: {e}")

if __name__ == "__main__":
    data_dir = "./data"
    os.makedirs(data_dir, exist_ok=True)

    # CICIDS2017 dataset
    # Using 'dhoogla/cicids2017' as it seems to be a common one.
    # If this doesn't work, try 'chethuhn/network-intrusion-dataset'
    download_dataset("dhoogla/cicids2017", os.path.join(data_dir, "cicids2017"))

    # GUIDE dataset - Microsoft Security Incident Prediction
    download_dataset("microsoft/microsoft-security-incident-prediction", os.path.join(data_dir, "guide"))


