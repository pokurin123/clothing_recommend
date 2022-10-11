from library_dir.func_box import self_func
import os
import time

time_sta = time.time()

# 自作ライブラリ
lib = self_func()

im_ = lib.remove_back("./static/images/input_image/test1.jpg")
print("ok1")
im_.save("./static/images/only_image/only_human.png")
lib.cutting_wear()
print("ok2")
# した3つユーザ選ぶ
which = "ボトムス"
select_img_path = "static/images/output_image/bottoms_box/bottoms_0.png"
concept = "天然素材"
sim_list = lib.get_sim_name(which,concept,select_img_path)
print(sim_list)
print("time:"+str(time.time()- time_sta))