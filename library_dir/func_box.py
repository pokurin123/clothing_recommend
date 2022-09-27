# returnで背景取り除いたPIL.Imageを返す
from rembg import remove
from PIL import Image, ImageDraw

class self_func:
    def remove_back(self,input_path):
        input_ = Image.open(input_path)
        input_resize = input_.resize((400, 600))
        remove_bg = remove(input_resize)
        bg_ = Image.new("RGBA", (400, 600), (125, 125, 125, 255))
        output_ = Image.alpha_composite(bg_, remove_bg)
        return output_