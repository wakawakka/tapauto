import requests
import code
from PIL import Image
import io


def rgb_to_hex(pix):
    r, g, b = pix
    r, g, b = int(r), int(g), int(b)
    # return hex((r << 16) + (g << 8) + b).replace('0x','#').upper()
    n = (r << 16) + (g << 8) + b
    return f"#{n:06X}"


def get_image_state(proxies=None):
    image_url = "https://image.notpx.app/api/v2/image"
    r = requests.get(image_url, proxies=proxies)
    if r.status_code == 200:
        img_io = io.BytesIO(r.content)
        img_io.seek(0)
    else:
        print(
            f"Fail to get image state (get request). Status: {r.status_code}, Error: {r.text}"
        )
        return False
    img = Image.open(img_io)
    return img


def get_job(img, location):
    img_pixels = img.load()
    init_x = location[0]
    init_y = location[1]

    world_picture = get_image_state(proxies=None)
    world_picture_pixels = world_picture.load()
    pixels_to_paint = []

    for x_pad in range(img.size[0]):
        for y_pad in range(img.size[1]):

            x, y = init_x + x_pad, init_y + y_pad
            # code.interact(local=locals())
            # print(x, y, img_pixels[x_pad, y_pad], world_picture_pixels[x, y])
            if img_pixels[x_pad, y_pad] == world_picture_pixels[x, y]:
                print(f"Same same {x}:{y}")
            else:
                print(
                    f"Need paint {x}:{y}. Ours: {img_pixels[x_pad, y_pad]}, Theirs: f{world_picture_pixels[x, y]}"
                )
                pixels_to_paint.append((x, y, img_pixels[x_pad, y_pad]))

    return pixels_to_paint
