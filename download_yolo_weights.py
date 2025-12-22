"""
Download YOLOv4-tiny weights for license plate detection
This script downloads pre-trained weights from the ALPR repository
"""
import os
import urllib.request
import sys


def download_file(url: str, output_path: str):
    """Download a file from URL with progress bar"""
    def progress_callback(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        sys.stdout.write(f"\rDownloading: {percent:.1f}%")
        sys.stdout.flush()
    
    print(f"Downloading from {url}")
    urllib.request.urlretrieve(url, output_path, progress_callback)
    print("\n✓ Download complete!")


def main():
    """Main download function"""
    # Create weights directory
    weights_dir = os.path.join("backend", "yolo_weights")
    os.makedirs(weights_dir, exist_ok=True)
    
    print("=" * 60)
    print("YOLOv4-tiny License Plate Detection Weights Downloader")
    print("=" * 60)
    print()
    
    # Note: These URLs are placeholders. You need to provide actual URLs
    # The ALPR repository doesn't have direct download links in the README
    # You would need to:
    # 1. Train your own model following the ALPR repository instructions
    # 2. Or use a pre-trained model from another source
    # 3. Or provide your own weights
    
    print("⚠️  Important: YOLOv4 weights for license plate detection need to be obtained separately.")
    print()
    print("Options:")
    print("1. Train your own model using the ALPR repository:")
    print("   https://github.com/BarthPaleologue/ALPR")
    print("   Training notebook: https://colab.research.google.com/drive/1zi0m3pE3KcWyKATRhqo4wTCSqglzLG3u")
    print()
    print("2. Use a pre-trained model from these datasets:")
    print("   - Romanian plates: https://github.com/RobertLucian/license-plate-dataset")
    print("   - French plates: https://github.com/qanastek/FrenchLicencePlateDataset")
    print("   - PP4AV (Paris + Strasbourg): https://huggingface.co/datasets/khaclinh/pp4av")
    print()
    print("3. Required files (place in backend/yolo_weights/):")
    print("   - yolov4-tiny-license-plate.weights")
    print("   - yolov4-tiny-license-plate.cfg")
    print()
    
    # Create example config file
    config_path = os.path.join(weights_dir, "yolov4-tiny-license-plate.cfg")
    if not os.path.exists(config_path):
        print("Creating example YOLOv4-tiny config file...")
        create_example_config(config_path)
        print(f"✓ Config file created at {config_path}")
        print("  You'll need to adjust this config based on your training setup.")
    
    print()
    print("=" * 60)
    print("Setup Instructions:")
    print("=" * 60)
    print("1. Obtain YOLOv4-tiny weights for license plate detection")
    print("2. Place weights file in: backend/yolo_weights/yolov4-tiny-license-plate.weights")
    print("3. Place config file in: backend/yolo_weights/yolov4-tiny-license-plate.cfg")
    print("4. The system will automatically detect and use them when available")
    print()
    
    # Check for alternative: use a generic darknet weights URL (example)
    print("Alternative: Download a generic YOLOv4-tiny model")
    response = input("Would you like to download a generic YOLOv4-tiny model? (y/n): ")
    
    if response.lower() == 'y':
        # Generic YOLOv4-tiny weights (not trained for license plates)
        weights_url = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"
        weights_path = os.path.join(weights_dir, "yolov4-tiny-generic.weights")
        
        cfg_url = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg"
        cfg_path = os.path.join(weights_dir, "yolov4-tiny-generic.cfg")
        
        try:
            print("\nDownloading generic YOLOv4-tiny weights...")
            download_file(weights_url, weights_path)
            
            print("\nDownloading generic YOLOv4-tiny config...")
            download_file(cfg_url, cfg_path)
            
            print("\n✓ Generic model downloaded successfully!")
            print("⚠️  Note: This model is NOT trained for license plates.")
            print("   It's provided as an example only.")
        except Exception as e:
            print(f"\n✗ Error downloading: {e}")
    
    print("\nFor best results, train or obtain a model specifically for license plate detection.")


def create_example_config(config_path: str):
    """Create an example YOLOv4-tiny config file"""
    config_content = """[net]
# Testing
batch=1
subdivisions=1
# Training
# batch=64
# subdivisions=16
width=256
height=160
channels=3
momentum=0.9
decay=0.0005
angle=0
saturation = 1.5
exposure = 1.5
hue=.1

learning_rate=0.00261
burn_in=1000
max_batches = 10000
policy=steps
steps=8000,9000
scales=.1,.1

[convolutional]
batch_normalize=1
filters=32
size=3
stride=2
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=64
size=3
stride=2
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=64
size=3
stride=1
pad=1
activation=leaky

[route]
layers=-1
groups=2
group_id=1

[convolutional]
batch_normalize=1
filters=32
size=3
stride=1
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=32
size=3
stride=1
pad=1
activation=leaky

[route]
layers = -1,-2

[convolutional]
batch_normalize=1
filters=64
size=1
stride=1
pad=1
activation=leaky

[route]
layers = -6,-1

[maxpool]
size=2
stride=2

[convolutional]
batch_normalize=1
filters=128
size=3
stride=1
pad=1
activation=leaky

[route]
layers=-1
groups=2
group_id=1

[convolutional]
batch_normalize=1
filters=64
size=3
stride=1
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=64
size=3
stride=1
pad=1
activation=leaky

[route]
layers = -1,-2

[convolutional]
batch_normalize=1
filters=128
size=1
stride=1
pad=1
activation=leaky

[route]
layers = -6,-1

[maxpool]
size=2
stride=2

[convolutional]
batch_normalize=1
filters=256
size=3
stride=1
pad=1
activation=leaky

[route]
layers=-1
groups=2
group_id=1

[convolutional]
batch_normalize=1
filters=128
size=3
stride=1
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=128
size=3
stride=1
pad=1
activation=leaky

[route]
layers = -1,-2

[convolutional]
batch_normalize=1
filters=256
size=1
stride=1
pad=1
activation=leaky

[route]
layers = -6,-1

[maxpool]
size=2
stride=2

[convolutional]
batch_normalize=1
filters=512
size=3
stride=1
pad=1
activation=leaky

##################################

[convolutional]
batch_normalize=1
filters=256
size=1
stride=1
pad=1
activation=leaky

[convolutional]
batch_normalize=1
filters=512
size=3
stride=1
pad=1
activation=leaky

[convolutional]
size=1
stride=1
pad=1
filters=18
activation=linear



[yolo]
mask = 3,4,5
anchors = 10,14,  23,27,  37,58,  81,82,  135,169,  344,319
classes=1
num=6
jitter=.3
scale_x_y = 1.05
cls_normalizer=1.0
iou_normalizer=0.07
iou_loss=ciou
ignore_thresh = .7
truth_thresh = 1
random=0
resize=1.5
nms_kind=greedynms
beta_nms=0.6

[route]
layers = -4

[convolutional]
batch_normalize=1
filters=128
size=1
stride=1
pad=1
activation=leaky

[upsample]
stride=2

[route]
layers = -1, 23

[convolutional]
batch_normalize=1
filters=256
size=3
stride=1
pad=1
activation=leaky

[convolutional]
size=1
stride=1
pad=1
filters=18
activation=linear

[yolo]
mask = 1,2,3
anchors = 10,14,  23,27,  37,58,  81,82,  135,169,  344,319
classes=1
num=6
jitter=.3
scale_x_y = 1.05
cls_normalizer=1.0
iou_normalizer=0.07
iou_loss=ciou
ignore_thresh = .7
truth_thresh = 1
random=0
resize=1.5
nms_kind=greedynms
beta_nms=0.6
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)


if __name__ == "__main__":
    main()
