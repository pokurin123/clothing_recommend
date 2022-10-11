"""
remove_back(input_path) : 入力画像パスを入れるとreturnで背景取り除いたPIL.Imageを返す
cutting_wear() : カットしたイメージをトップス、ボトムスに分けてdirにアップデート
get_sim_name(which,concept,targe_path) : 類似画像のpath(A1.png)を配列で10個返す
get_detail(self,natural_id) : A1みたいなnatural_idを入れると詳細を返す
get_like(self,id_) : idを入れるといいね悪いね数を返す
"""

from rembg import remove
from PIL import Image, ImageDraw
from library_dir.fashion_cutting.new_image_demo import detect_class
import psycopg2
import glob
import cv2
import numpy as np

# postgreSQL呼び出し用
conn = psycopg2.connect(\
    "host=localhost \
    port=5432 \
    dbname=clothing_recommend \
    user=postgres \
    password="\
        )

# 画像カット用
cutting_lib = detect_class()

# 画像リサイズ用関数
def keepAspectResize(img_, width, height):
    x_ratio = width / img_.width
    y_ratio = height / img_.height
    if x_ratio < y_ratio:
        re_size = (width, round(img_.height * x_ratio))
    else:
        re_size = (round(img_.width * y_ratio), height)
    resized_image = img_.resize(re_size)
    return resized_image, re_size
# 画像に余白を入れてリサイズするやつ
def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result
# 比較に必要な画像pathを抽出するやつ
def get_nat(x):
    return ["static/images/image_storage/cutting_box/cut_" + x[0] + ".png",x[1]]
# ハッシュ平均計算用
def average_hash(target_file, size):
    img = Image.open(target_file)
    img = img.convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
    px = np.array(img).reshape((size, size, 3))
    avg = px.mean()
    px = 1 * (px > avg)
    return px
# ハッシュの距離を求める
def hamming_dist(a, b):    
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    dist = (a != b).sum()
    return dist

class self_func:
    # 入力画像を入れると背景を取り除いたPIL.Imageをreturn
    def remove_back(self,input_path):
        input_ = Image.open(input_path)
        input_resize, resize_size = keepAspectResize(input_, 500, 500)
        remove_bg = remove(input_resize)
        bg_ = Image.new("RGBA", resize_size, (125, 125, 125, 255))
        output_ = Image.alpha_composite(bg_, remove_bg)
        output_resize = expand2square(output_, (125, 125, 125)).resize((500, 500))
        return output_resize
    # tops, bottomsごとに画像を切り取ってimages配下dirに配置、only_image(人抽出画像)は削除してくれてる
    def cutting_wear(self):
        cutting_lib.detect_wear("./static/images/only_image")
    # 画像の類似度計算 カテゴリー,コンセプト,比較画像pathを入力すると近いやつ10個返してくれる
    def get_sim_name(self,which,concept,targe_path):
        # 特徴点用
        target_img = cv2.imread(targe_path)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        detector = cv2.AKAZE_create()
        (target_kp, target_des) = detector.detectAndCompute(target_img, None)

        # ハッシュ用
        size = 64
        target_ = targe_path
        target_dist = average_hash(target_, size)

        cur = conn.cursor()
        cur.execute("SELECT natural_id,コンセプト FROM clothing_box where カテゴリー = '"+which+"'")
        get_table = cur.fetchall()
        cur.close()
        # conn.close()
        wanna_imgs = list(map(get_nat,get_table))

        sim_hash_dict = {}
        sim_point_dict = {}
        sum_score = {}
        concept_dict = {}
        for file in wanna_imgs:
            #比較対象の写真の特徴点を検出
            try:
                comparing_img = cv2.imread(file[0], cv2.IMREAD_GRAYSCALE)
                (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
                # BFMatcherで総当たりマッチングを行う
                matches = bf.match(target_des, comparing_des)
                #特徴量の距離を出し、平均を取る
                dist = [m.distance for m in matches]
                ret = sum(dist) / len(dist)
            except cv2.error:
                # cv2がエラーを吐いた場合の処理
                ret = 100000
            sim_point_dict[file[0][44:]] = ret
            try:
                dist = average_hash(file[0], size)
                diff = hamming_dist(target_dist, dist) / 256
            except:
                diff = 100000
            sim_hash_dict[file[0][44:]] = diff
            try:
                if file[1] == concept:
                    score = sim_point_dict[file[0][44:]]*0.2 + sim_hash_dict[file[0][44:]] - 15
                else:
                    score = sim_point_dict[file[0][44:]]*0.2 + sim_hash_dict[file[0][44:]]
            except:
                score = 999999
            sum_score[file[0][44:]] = score
            concept_dict[file[0][44:]] = file[1]
        res_dict = list(dict(sorted(sum_score.items(), key=lambda x:x[1])).keys())[:10]
        return res_dict
    # 画像のdetailデータを返す
    def get_detail(self,natural_id):
        cur = conn.cursor()
        cur.execute("SELECT * FROM clothing_box where natural_id = '"+natural_id+"'")
        get_table = cur.fetchall()
        cur.close()
        # conn.close()
        return get_table[0]
    # 画像のいいね悪いねを返す
    def get_like(self,id_):
        cur = conn.cursor()
        cur.execute("SELECT good,bad FROM good_bad_table where id = '"+str(id_)+"'")
        get_table = cur.fetchall()
        cur.close()
        # conn.close()
        return get_table[0]
    # 画像のいいね悪いねに+1
    def add_like(self,id_,which):
        cur = conn.cursor()
        cur = conn.cursor()
        cur.execute("SELECT good,bad FROM good_bad_table where id = '"+str(id_)+"'")
        get_table = cur.fetchall()
        cur.close()
        if which == "good":
            now_ = get_table[0][0] + 1
        else:
            now_ = get_table[0][1] + 1
        cur = conn.cursor()
        cur.execute("UPDATE good_bad_table SET "+which+" = "+str(now_)+" WHERE id = "+str(id_))
        conn.commit()
        cur.close()
        # conn.close()
        return "ok"