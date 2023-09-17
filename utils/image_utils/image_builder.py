from PIL import Image, ImageDraw, ImageFont
from typing import Literal, Union, Tuple, List, Dict, Any, Optional
from pathlib import Path

from io import BytesIO
from base64 import b64encode

from configs.path_config import FONT_PATH

from .types import ColorType, PosTypeInt, FontStyle, FontWeight

# 用于便捷生成图片的类


class ImageBuilder:
    """
    快捷生成图片。也用作基类
    """

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.image_now = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image_now)

    def paste_image(
        self,
        image: Union["ImageBuilder", Image.Image, BytesIO],
        offset: Tuple[int, int] = (0, 0),
        align: Tuple[
            Literal["left", "center", "right"], Literal["top", "center", "bottom"]
        ] = ("left", "top"),
    ):
        """
        description:
            将图片粘贴到画布上。默认粘贴到左上角
        params:
            :param image: 要粘贴的图片
            :param offset: 粘贴的偏移
            :param align: 粘贴的对齐方式
        """
        if isinstance(image, ImageBuilder):
            image = image.image_now

        x = {
            "left": 0,
            "center": (self.w - image.width) // 2,
            "right": self.w - image.width,
        }[align[0]]
        y = {
            "top": 0,
            "center": (self.h - image.height) // 2,
            "bottom": self.h - image.height,
        }[align[1]]
        x, y = x + offset[0], y + offset[1]
        self.image_now.paste(image, (x, y), image)

    def join_image(
        self,
        image: Union["ImageBuilder", Image.Image, BytesIO],
        side: Literal["left", "right"] = "right",
        align: Literal["top", "center", "bottom"] = "center",
        spacing: int = 0,
        y_offset: int = 0,
    ):
        """
        description:
            拼接另一张图片。仅支持水平拼接
        params:
            :param image: 要拼接的图片
            :param side: 拼接方向。可选值为 "left", "right"
            :param align: 拼接对齐方式。可选值为 "top", "center", "bottom"
            :param spacing: 两张图片间距
            :param y_offset: 在 align 基础上的 y 轴偏移量
        """
        if isinstance(image, Image.Image) or isinstance(image, BytesIO):
            image = ImageBuilder_Photo(image)
        # 自动扩大画布
        if align == "top":
            y = y_offset + 0
        elif align == "center":
            y = y_offset + (self.h - image.h) // 2
        elif align == "bottom":
            y = y_offset + self.h - image.h
        self_y = 0
        if y < 0:
            self_y = -y
            y = 0
        self.w += image.w + spacing
        self.h = max(self.h + self_y, image.h + y)

        new_image = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        if side == "right":
            new_image.paste(self.image_now, (0, self_y))
            new_image.paste(image.image_now, (self.w - image.w, y))
        elif side == "left":
            new_image.paste(self.image_now, (image.w + spacing, self_y))
            new_image.paste(image.image_now, (0, y))
        self.image_now = new_image
        self.draw = ImageDraw.Draw(self.image_now)

    def join_image_vertical(
        self,
        image: Union["ImageBuilder", Image.Image, BytesIO],
        side: Literal["top", "bottom"] = "bottom",
        align: Literal["left", "center", "right"] = "left",
        spacing: int = 0,
        x_offset: int = 0,
    ):
        """
        description:
            拼接另一张图片。仅支持垂直拼接
        params:
            :param image: 要拼接的图片
            :param side: 拼接方向。可选值为 "top", "bottom"
            :param align: 拼接对齐方式。可选值为 "left", "center", "right"
            :param spacing: 两张图片间距
            :param x_offset: 在 align 基础上的 x 轴偏移量
        """
        if isinstance(image, Image.Image) or isinstance(image, BytesIO):
            image = ImageBuilder_Photo(image)
        if align == "left":
            x = x_offset + 0
        elif align == "center":
            x = x_offset + (self.w - image.w) // 2
        elif align == "right":
            x = x_offset + self.w - image.w
        self_x = 0
        if x < 0:
            self_x = -x
            x = 0
        self.h += image.h + spacing
        self.w = max(self.w + self_x, image.w + x)

        new_image = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        if side == "bottom":
            new_image.paste(self.image_now, (self_x, 0))
            new_image.paste(image.image_now, (x, self.h - image.h))
        elif side == "top":
            new_image.paste(self.image_now, (self_x, image.h + spacing))
            new_image.paste(image.image_now, (x, 0))
        self.image_now = new_image
        self.draw = ImageDraw.Draw(self.image_now)

    def draw_points(
        self,
        pos: List[Tuple[int, int]],
        color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    ):
        """
        description:
            在画布上画点
        params:
            :param pos: 点的位置
            :param color: 点的颜色
            :param width: 点的大小
        """
        self.draw.point(pos, color)

    def resize(self, *, ratio: float = 0, w: int = 0, h: int = 0):
        """
        description:
            伸缩图片。ratio 优先级最高。三个参数只需要一个
        params:
            :param ratio: 伸缩比例
            :param w: 伸缩至宽度
            :param h: 伸缩至高度
        """
        if not ratio and not w and not h:
            raise ValueError("伸缩图片至少需要一个参数")
        if ratio:
            w = int(self.w * ratio)
            h = int(self.h * ratio)
            self.image_now = self.image_now.resize((w, h))
        else:
            if not w:
                w = self.w * h // self.h
            elif not h:
                h = self.h * w // self.w
            self.image_now = self.image_now.resize((w, h))
        self.w = w
        self.h = h
        self.draw = ImageDraw.Draw(self.image_now)

    def extend_to_size(
        self,
        w: int = None,
        h: int = None,
        *,
        align: Tuple[
            Literal["left", "center", "right"], Literal["top", "center", "bottom"]
        ] = ("left", "top"),
    ):
        """
        description:
            扩展画布大小
        params:
            :param w: 宽度。默认为原宽度
            :param h: 高度。默认为原高度
            :param align: 对齐方式
        """
        if not w and not h:
            raise ValueError("扩展画布大小至少需要一个参数")
        w = self.w if not w else w
        h = self.h if not h else h
        if self.w > w or self.h > h:
            raise ValueError("图片大小不能大于扩展后的大小")
        new_image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x = {
            "left": 0,
            "center": (w - self.w) // 2,
            "right": w - self.w,
        }[align[0]]
        y = {
            "top": 0,
            "center": (h - self.h) // 2,
            "bottom": h - self.h,
        }[align[1]]
        new_image.paste(self.image_now, (x, y))
        self.image_now = new_image
        self.w, self.h = w, h
        self.draw = ImageDraw.Draw(self.image_now)

    def rotate(self, angle: float, expand: bool = True):
        """
        description:
            旋转图片
        params:
            :param angle: 旋转角度
            :param expand: 是否扩展画布
        """
        self.image_now = self.image_now.rotate(angle, expand=expand)
        self.w, self.h = self.image_now.size
        self.draw = ImageDraw.Draw(self.image_now)

    def cut_and_resize(self, w: int, h: int):
        """
        description:
            先缩放再裁剪，以达成 w*h 的大小
        params:
            :param w: 宽度
            :param h: 高度
        """
        ratio = max(w / self.w, h / self.h)
        self.resize(ratio=ratio)
        self.image_now = self.image_now.crop((0, 0, w, h))
        self.w, self.h = self.image_now.size
        self.draw = ImageDraw.Draw(self.image_now)

    def cut_to_circle(self):
        """
        description:
            将图片裁剪为圆形。圆心为图片中心，半径为图片宽高中较小的一半
        """
        mask = Image.new("L", (self.w, self.h), 0)
        diameter = min(self.w, self.h)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse(
            (
                (self.w - diameter) // 2,
                (self.h - diameter) // 2,
                (self.w + diameter) // 2,
                (self.h + diameter) // 2,
            ),
            fill=255,
        )
        self.image_now.putalpha(mask)

    def save(self, path: str):
        """
        description:
            保存图片
        params:
            :param path: 保存路径
        """
        self.image_now.save(path)

    def pure_color_background(self, color: Tuple[int, int, int, int] = None):
        """
        description:
            将图片背景改为纯色
        params:
            :param color: 背景颜色
        """
        color = color or (255, 255, 255, 255)
        # 创建纯色背景，使用 paste 方法
        new_image = Image.new("RGBA", (self.w, self.h), color)
        new_image.paste(self.image_now, (0, 0), self.image_now)
        self.image_now = new_image
        self.draw = ImageDraw.Draw(self.image_now)

    def get_byte_png(self) -> BytesIO:
        """
        description:
            获得 png
        """
        output = BytesIO()
        self.image_now.save(output, format="PNG")
        return output

    def to_base64(self, decode: bool = False):
        """
        description:
            将图片转换为 base64
        """
        buffered = BytesIO()
        self.image_now.save(buffered, format="PNG")
        img_str = b64encode(buffered.getvalue())
        if decode:
            return img_str.decode("utf-8")
        return img_str


class ImageBuilder_Text(ImageBuilder):
    """
    生成文字图片
    """

    def __init__(
        self,
        text: str,
        font_size: int = 40,
        color: Tuple[int, int, int, int] = (0, 0, 0, 255),
        font: str = "msyh.ttf",
        *,
        style: Literal["normal", "bold", "italic"] = "normal",
        weight: Literal["normal", "bold"] = "normal",
        spacing: int = 4,
        align: Literal["left", "center", "right"] = "left",
        stroke_width: int = 0,
        stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
        warp_width: int = 0,
        warp_spacing: int = 4,
    ):
        """
        description:
            生成文字图片
        params:
            :param text: 文字
            :param font_size: 字体大小
            :param font: 字体。默认为 font.ttf
            :param color: 字体颜色。要求为 RGBA 格式，即 (r, g, b, a)
            :param style: 字体样式。可选值为 "normal", "bold", "italic"
            :param weight: 字体粗细。可选值为 "normal", "bold"
            :param spacing: 多行文字间距
            :param align: 文字对齐方式。可选值为 "left", "center", "right"
            :param stroke_width: 描边宽度
            :param stroke_color: 描边颜色。要求为 RGBA 格式，即 (r, g, b, a)
            :param warp_width: 自动换行宽度。为 0 时不自动换行
            :param warp_spacing: 自动换行间距
        """

        def draw_text(text: str):
            # 将换行符替换为可以显示的字符 \n
            text = text.replace("\n", "\\n")
            
            w, h = self.font.getsize(text)
            image = ImageBuilder(w, h)
            image.draw.text(
                (0, 0),
                text,
                self.color,
                font=self.font,
                style=style,
                weight=weight,
                spacing=spacing,
                align=align,
                stroke_width=stroke_width,
                stroke_fill=stroke_color,
            )
            return image

        def text_warp(text: str):
            text_list = []
            text_now = ""
            for i in text:
                if i == "\n":
                    text_list.append(text_now)
                    text_now = ""
                    continue
                if self.font.getsize(text_now)[0] > warp_width - warp_spacing * (
                    len(text_now) - 1
                ):
                    text_list.append(text_now)
                    text_now = ""
                text_now += i
            text_list.append(text_now)
            return text_list

        self.font = ImageFont.truetype(str(FONT_PATH / font), font_size)
        self.text = text
        self.color = color
        if not warp_width:
            self.image_now = draw_text(text).image_now
            self.w, self.h = self.image_now.size
            self.draw = ImageDraw.Draw(self.image_now)
        else:
            text_list = text_warp(text)
            self.image_now = draw_text(text_list[0]).image_now
            self.w, self.h = self.image_now.size
            self.draw = ImageDraw.Draw(self.image_now)
            for i in text_list[1:]:
                self.join_image_vertical(draw_text(i), spacing=warp_spacing)
            self.extend_to_size(warp_width, self.h)


class ImageBuilder_Photo(ImageBuilder):
    """
    读取图片
    """

    def __init__(self, image: Union[str, Path, BytesIO, Image.Image]):
        """
        description:
            读取图片
        params:
            :param image: 图片文件路径或 BytesIO 对象
        """
        if isinstance(image, Image.Image):
            self.image_now = image
        else:
            self.image_now = Image.open(image)
        self.w, self.h = self.image_now.size
        self.draw = ImageDraw.Draw(self.image_now)
