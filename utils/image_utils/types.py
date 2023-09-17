

from typing import Literal, Tuple, Union

ColorType = Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
PosTypeInt = Tuple[int, int]

FontStyle = Literal["normal", "italic", "oblique"]
FontWeight = Literal["ultralight", "light", "normal", "bold", "ultrabold", "heavy"]