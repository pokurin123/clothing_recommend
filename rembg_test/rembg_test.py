from rembg import remove
from PIL import Image

input_path = 'images/test1.jpg'
output_path = 'output2.png'

input = Image.open(input_path)
output = remove(input)
print(type(output))