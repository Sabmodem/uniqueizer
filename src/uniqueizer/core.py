import io
import logging
import random
from typing import TypeGuard, Union
from PIL import Image, ImageFile, ImageEnhance, ImageFilter
from .entities import (
    ImageOperation, UniqueizationType, Crop, Resize, Rotate,
    TransformOperation, TransposeOperation, ConvertOperation,
    EnhanceOperation, SimpleFilterOperation, PixelNoiseOperation,
    UniqueizationSettings, EnhanceMethod, SimpleFilterMethod
)

def is_crop(op: ImageOperation) -> TypeGuard[Crop]: return op.type == UniqueizationType.CROP
def is_resize(op: ImageOperation) -> TypeGuard[Resize]: return op.type == UniqueizationType.RESIZE
def is_rotate(op: ImageOperation) -> TypeGuard[Rotate]: return op.type == UniqueizationType.ROTATE
def is_transform(op: ImageOperation) -> TypeGuard[TransformOperation]: return op.type == UniqueizationType.TRANSFORM
def is_transpose(op: ImageOperation) -> TypeGuard[TransposeOperation]: return op.type == UniqueizationType.TRANSPOSE
def is_convert(op: ImageOperation) -> TypeGuard[ConvertOperation]: return op.type == UniqueizationType.CONVERT
def is_enhance(op: ImageOperation) -> TypeGuard[EnhanceOperation]: return op.type == UniqueizationType.ENHANCE
def is_simple_filter(op: ImageOperation) -> TypeGuard[SimpleFilterOperation]: return op.type == UniqueizationType.SIMPLE_FILTER
def is_pixel_noise(op: ImageOperation) -> TypeGuard[PixelNoiseOperation]: return op.type == UniqueizationType.PIXEL_NOISE

def calculate_average_color(img: Image.Image):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    num_pixels = img.width * img.height
    pixels = list(img.getdata())
    return (
        int(sum(p[0] for p in pixels) / num_pixels),
        int(sum(p[1] for p in pixels) / num_pixels),
        int(sum(p[2] for p in pixels) / num_pixels)
    )

class PhotoUniquezer:
    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)

    def uniqueze(self, image_input: Union[bytes, str, io.BytesIO, Image.Image], settings: UniqueizationSettings) -> Image.Image:
        if isinstance(image_input, (bytes, io.BytesIO)):
            img = Image.open(image_input if isinstance(image_input, io.BytesIO) else io.BytesIO(image_input))
        elif isinstance(image_input, str):
            img = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            img = image_input.copy()
        else:
            raise ValueError("Unsupported input type.")

        for setting in settings.settings:
            self._logger.info(f'APPLYING OPERATION: {setting.type}')
            if is_crop(setting):
                w, h = img.size
                img = img.crop((setting.left, setting.top, w - setting.right, h - setting.bottom))

            elif is_resize(setting):
                img = img.resize((setting.width, setting.height), resample=setting.resample)

            elif is_rotate(setting):
                if setting.blurred_background:
                    if img.mode in ('P', 'LA', 'L'):
                        img = img.convert('RGB')
                    img_blurred = img.filter(ImageFilter.GaussianBlur(setting.blurred_background_blur_radius))
                    img_fg = img.convert('RGBA').rotate(
                        setting.angle, resample=setting.resample, expand=setting.expand,
                        center=setting.center, fillcolor=(0, 0, 0, 0)
                    )
                    img_blurred_resized = img_blurred.resize(img_fg.size, Image.Resampling.LANCZOS)
                    img_blurred_resized.paste(img_fg, (0, 0), mask=img_fg)
                    img = img_blurred_resized
                else:
                    if setting.fill_with_average_color:
                        setting.fillcolor = calculate_average_color(img)
                    img = img.rotate(setting.angle, resample=setting.resample, expand=setting.expand, center=setting.center, fillcolor=setting.fillcolor)

            elif is_transform(setting):
                fill = hasattr(setting, "fillcolor")
                img = img.transform(img.size, setting.method, setting.data, setting.resample, fill, setting.fillcolor)

            elif is_transpose(setting):
                img = img.transpose(setting.transpose)

            elif is_convert(setting):
                img = img.convert(setting.mode, setting.matrix, dither=setting.dither, palette=setting.palette, colors=setting.colors)

            elif is_enhance(setting):
                if setting.method == EnhanceMethod.CONTRAST: img = ImageEnhance.Contrast(img).enhance(setting.factor)
                elif setting.method == EnhanceMethod.BRIGHTNESS: img = ImageEnhance.Brightness(img).enhance(setting.factor)
                elif setting.method == EnhanceMethod.SHARPNESS: img = ImageEnhance.Sharpness(img).enhance(setting.factor)
                elif setting.method == EnhanceMethod.COLOR: img = ImageEnhance.Color(img).enhance(setting.factor)

            elif is_simple_filter(setting):
                filters = {
                    SimpleFilterMethod.CONTOUR: ImageFilter.CONTOUR,
                    SimpleFilterMethod.EDGE_ENHANCE: ImageFilter.EDGE_ENHANCE,
                    SimpleFilterMethod.EDGE_ENHANCE_MORE: ImageFilter.EDGE_ENHANCE_MORE,
                    SimpleFilterMethod.EMBOSS: ImageFilter.EMBOSS,
                    SimpleFilterMethod.FIND_EDGES: ImageFilter.FIND_EDGES,
                    SimpleFilterMethod.SHARPEN: ImageFilter.SHARPEN,
                    SimpleFilterMethod.SMOOTH: ImageFilter.SMOOTH,
                    SimpleFilterMethod.SMOOTH_MORE: ImageFilter.SMOOTH_MORE,
                }
                if setting.method in filters:
                    img = img.filter(filters[setting.method])

            elif is_pixel_noise(setting):
                num_pixels = random.randint(setting.pixels_min, setting.pixels_max)
                w, h = img.size
                img_temp = img.convert('RGB') if img.mode == 'RGBA' else img.copy()
                alpha = img.split()[-1] if img.mode == 'RGBA' else None
                pixels = img_temp.load()

                for _ in range(num_pixels):
                    if w > 0 and h > 0:
                        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
                        pixels[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                img = img_temp
                if alpha:
                    img.putalpha(alpha)

        return img
