# uniqueizer

Core PIL image uniqueization pipeline.

## Installation

```bash
uv sync
```

## Usage

```python
from PIL import Image, ImageFilter
from uniqueizer import (
    PhotoUniquezer,
    UniqueizationSettings,
    Rotate,
    Crop,
    Resize,
    EnhanceOperation,
    EnhanceMethod,
)

uniquezer = PhotoUniquezer()

settings = UniqueizationSettings(
    settings=[
        Rotate(angle=45.0),
        Crop(left=10, top=10, right=20, bottom=20),
        Resize(width=800, height=600),
        EnhanceOperation(method=EnhanceMethod.CONTRAST, factor=1.5),
    ]
)

image = Image.open("input.jpg")
result = uniquezer.uniqueze(image, settings)
result.save("output.jpg")
```

## Operations

### Rotate
- `angle`: Rotation angle in degrees
- `expand`: Expand canvas to fit rotated image
- `fillcolor`: Fill color for transparent areas
- `fill_with_average_color`: Auto-fill with average image color
- `blurred_background`: Create blurred background effect
- `blurred_background_blur_radius`: Blur radius for background

### Crop
- `left`, `top`, `right`, `bottom`: Crop margins

### Resize
- `width`, `height`: Target dimensions
- `resample`: Resampling filter (default: NEAREST)

### Transpose
- `transpose`: Transpose operation (e.g., FLIP_LEFT_RIGHT)

### Transform
- `method`: Transform method
- `data`: Transform data tuple

### Convert
- `mode`: Target color mode
- `matrix`: Color conversion matrix
- `dither`: Dither method
- `palette`, `colors`: Palette settings

### Enhance
- `method`: CONTRAST, BRIGHTNESS, SHARPNESS, or COLOR
- `factor`: Enhancement factor

### Simple Filter
- `method`: CONTOUR, EDGE_ENHANCE, EMBOSS, FIND_EDGES, SHARPEN, SMOOTH, etc.

### Pixel Noise
- `pixels_min`, `pixels_max`: Random pixel modification range

## Development

This project uses `uv` as the package manager.

```bash
uv run python main.py
```
