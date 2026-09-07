from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Tuple, Any
import abc
from PIL.Image import Resampling, Transform, Transpose, Dither, Palette

class UniqueizationType(StrEnum):
    ROTATE = "rotate"
    CROP = "crop"
    RESIZE = "resize"
    TRANSFORM = "transform"
    TRANSPOSE = "transpose"
    CONVERT = "convert"
    ENHANCE = "enhance"
    SIMPLE_FILTER = "simple_filter"
    PIXEL_NOISE = "pixel_noise"

class EnhanceMethod(StrEnum):
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SHARPNESS = "sharpness"
    COLOR = "color"

class SimpleFilterMethod(StrEnum):
    BLUR = "Blur"
    CONTOUR = "Contour"
    DETAIL = "Detail"
    EDGE_ENHANCE = "Edge-enhancement"
    EDGE_ENHANCE_MORE = "Edge-enhancement More"
    EMBOSS = "Emboss"
    FIND_EDGES = "Find Edges"
    SHARPEN = "Sharpen"
    SMOOTH = "Smooth"
    SMOOTH_MORE = "Smooth More"

@dataclass
class ImageOperation(abc.ABC):
    type: UniqueizationType

@dataclass
class Rotate(ImageOperation):
    angle: float
    expand: bool = False
    fillcolor: Tuple[int, int, int] | None = None
    fill_with_average_color: bool = False
    blurred_background: bool = False
    blurred_background_blur_radius: int = 10
    center: Tuple[int, int] | None = None
    resample: Resampling = Resampling.NEAREST
    type: UniqueizationType = field(default=UniqueizationType.ROTATE, init=False)

@dataclass
class Crop(ImageOperation):
    left: int
    top: int
    right: int
    bottom: int
    type: UniqueizationType = field(default=UniqueizationType.CROP, init=False)

@dataclass
class Resize(ImageOperation):
    width: int
    height: int
    resample: Resampling = Resampling.NEAREST
    type: UniqueizationType = field(default=UniqueizationType.RESIZE, init=False)

@dataclass
class TransposeOperation(ImageOperation):
    transpose: Transpose
    type: UniqueizationType = field(default=UniqueizationType.TRANSPOSE, init=False)

@dataclass
class TransformOperation(ImageOperation):
    method: Transform
    data: Tuple[Any, ...]
    resample: Resampling = Resampling.NEAREST
    fillcolor: Tuple[int, int, int] | None = None
    type: UniqueizationType = field(default=UniqueizationType.TRANSFORM, init=False)

@dataclass
class ConvertOperation(ImageOperation):
    mode: str | None = None
    matrix: tuple[float, ...] | None = None
    dither: Dither | None = None
    palette: Palette = Palette.WEB
    colors: int = 256
    type: UniqueizationType = field(default=UniqueizationType.CONVERT, init=False)

@dataclass
class EnhanceOperation(ImageOperation):
    method: EnhanceMethod
    factor: float
    type: UniqueizationType = field(default=UniqueizationType.ENHANCE, init=False)

@dataclass
class SimpleFilterOperation(ImageOperation):
    method: SimpleFilterMethod
    type: UniqueizationType = field(default=UniqueizationType.SIMPLE_FILTER, init=False)

@dataclass
class PixelNoiseOperation(ImageOperation):
    pixels_min: int
    pixels_max: int
    type: UniqueizationType = field(default=UniqueizationType.PIXEL_NOISE, init=False)

@dataclass
class UniqueizationSettings:
    settings: List[ImageOperation]
