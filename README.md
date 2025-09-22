# image-watermark-tool，second commit
A command-line tool to add date watermark from EXIF metadata to images.

## Features
- Reads EXIF metadata from images to extract the shooting date
- Adds the date as a watermark on images
- Supports custom font size, color, and position
- Processes both single image files and entire directories
- Saves watermarked images to a separate directory

## Requirements
- Python 3.x
- Pillow library

## Installation
1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```
python watermark_tool.py <input_path>
```
Where `<input_path>` can be a single image file or a directory containing images.

### Custom Options
```
python watermark_tool.py <input_path> --font-size <size> --color <color> --position <position>
```

#### Available Options
- `--font-size <size>`: Set the font size of the watermark (default: 30)
- `--color <color>`: Set the font color (default: white)
  - Color can be specified as a named color (e.g., 'red', 'blue', 'black')
  - Or as a hexadecimal value (e.g., '#FF0000' for red)
  - Or as RGB values (e.g., '255,0,0' for red)
- `--position <position>`: Set the position of the watermark (default: bottom-right)
  - Available positions: top-left, top-right, bottom-left, bottom-right, center

## Examples

### Single Image
```
python watermark_tool.py photo.jpg
```

### Entire Directory
```
python watermark_tool.py photos_directory
```

### Custom Settings
```
python watermark_tool.py photo.jpg --font-size 40 --color red --position center
```

## Output
- When processing a single file, the watermarked image is saved with `_watermark` suffix in the same directory
- When processing a directory, watermarked images are saved to a new directory named `<original_dir>_watermark`

## Notes
- The tool will automatically extract the date from EXIF metadata (preferably DateTimeOriginal)
- If no valid EXIF date is found, the image will be skipped
- The watermark includes a semi-transparent background for better visibility on various image backgrounds
- Supported image formats: JPG, JPEG, PNG, BMP, GIF, TIFF
