from rembg import remove
from PIL import Image, ImageDraw

input_path = 'images/test1.jpg'
output_path = 'rembg_test/result/output2.png'

input_ = Image.open(input_path)
input_resize = input_.resize((400, 600))
remove_bg = remove(input_resize)

bg_ = Image.new("RGBA", (400, 600), (125, 125, 125, 255))

output_ = Image.alpha_composite(bg_, remove_bg)
output_.save(output_path)