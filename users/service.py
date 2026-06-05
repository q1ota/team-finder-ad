import io
import random
import re

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_SIZE, AvatarColor


def generate_avatar(letter: str) -> ContentFile:
    size = (AVATAR_SIZE, AVATAR_SIZE)
    font_size = AVATAR_SIZE // 2
    color = random.choice(list(AvatarColor))
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
    except OSError:
        font = ImageFont.load_default(size=font_size)

    text = letter.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size[0] - text_w) / 2 - bbox[0]
    y = (size[1] - text_h) / 2 - bbox[1]
    draw.text((x, y), text, fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())


def normalize_phone(phone: str):
    phone = phone.strip()
    if re.fullmatch(r'8\d{10}', phone):
        return '+7' + phone[1:]
    if re.fullmatch(r'\+7\d{10}', phone):
        return phone
    return None


def paginate(queryset, per_page, request):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))
