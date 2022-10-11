from library_dir.func_box import self_func
import os

# 自作ライブラリ
lib = self_func()

# im_ = lib.remove_back("./images/image_storage/natural_box/blue_test.jpeg")
# print("ok1")
# im_.save("blue_cut_test.png")

files = os.listdir("./images/image_storage/natural_box")
for file in files:
    im_ = lib.remove_back("./images/image_storage/natural_box/"+file)
    im_.save("./images/image_storage/cutting_box/cut_"+file)