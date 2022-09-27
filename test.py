from library_dir.func_box import self_func

# 自作ライブラリ
lib = self_func()

im_ = lib.remove_back("images/test2.jpg")
im_.save("output2.png")