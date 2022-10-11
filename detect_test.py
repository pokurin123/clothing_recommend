import cv2
import time
import psycopg2
from PIL import Image, ImageDraw
import os
from numpy import *
import numpy as np
# img1 = cv2.imread("images/image_storage/cutting_box/cut_A1.png") 
# gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY) 
# # ２枚目の画像をグレースケールで読み出し
# # gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY) 
# time_sta = time.time()
# # AKAZE検出器の生成
# akaze = cv2.AKAZE_create() 
# # gray1にAKAZEを適用、特徴点を検出
# kp1, des1 = akaze.detectAndCompute(gray1,None) 
# # gray2にAKAZEを適用、特徴点を検出
# kp2, des2 = akaze.detectAndCompute(gray2,None) 
# print(time.time()- time_sta)
# print(len(kp1))
# print(len(des1))

##############################################
def get_nat(x):
    return "images/image_storage/cutting_box/cut_" + x[0] + ".png"

# 画像データをAverage hashに変換
def average_hash(target_file, size):
    img = Image.open(target_file)
    img = img.convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
    px = np.array(img).reshape((size, size, 3))
    avg = px.mean()
    px = 1 * (px > avg)
    return px

def hamming_dist(a, b):    
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    dist = (a != b).sum()
    return dist

which = "ボトムス"
conn = psycopg2.connect(\
    "host=localhost \
    port=5432 \
    dbname=clothing_recommend \
    user=postgres \
    password="\
        )

# 特徴点用
target_img = cv2.imread("images/output_image/bottoms_box/bottoms_0.png")
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
detector = cv2.AKAZE_create()
(target_kp, target_des) = detector.detectAndCompute(target_img, None)

# ハッシュ用
size = 64
target_ = "images/output_image/bottoms_box/bottoms_0.png"
target_dist = average_hash(target_, size)

cur = conn.cursor()
cur.execute("SELECT natural_id FROM clothing_box where カテゴリー = '"+which+"'")
get_table = cur.fetchall()
cur.close()
conn.close()
wanna_imgs = list(map(get_nat,get_table))

sim_hash_dict = {}
sim_point_dict = {}
sum_score = {}
for file in wanna_imgs:
    #比較対象の写真の特徴点を検出
    try:
        comparing_img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
        # BFMatcherで総当たりマッチングを行う
        matches = bf.match(target_des, comparing_des)
        #特徴量の距離を出し、平均を取る
        dist = [m.distance for m in matches]
        ret = sum(dist) / len(dist)
    except cv2.error:
        # cv2がエラーを吐いた場合の処理
        ret = 100000
    sim_point_dict[file[37:]] = ret
    try:
        dist = average_hash(file, size)
        diff = hamming_dist(target_dist, dist) / 256
    except:
        diff = 100000
    sim_hash_dict[file[37:]] = diff
    try:
        score = sim_point_dict[file[37:]]*0.2 + sim_hash_dict[file[37:]]
    except:
        score = 999999
    sum_score[file[37:]] = score
res_dict = list(dict(sorted(sum_score.items(), key=lambda x:x[1])).keys())[:10]
print(sim_hash_dict)
print(res_dict)

########################################
# cur = conn.cursor()
# cur.execute("SELECT natural_id FROM clothing_box where カテゴリー = '"+which+"'")
# get_table = cur.fetchall()
# cur.close()
# conn.close()
# wanna_imgs = list(map(get_nat,get_table))

# size = 64  #圧縮サイズの指定
# target_file = "images/output_image/bottoms_box/bottoms_0.png" #類似検索対象の画像
# # search_dir = r"C:\Users\user\scrp\data\img"   #検索対象の画像（約5000枚）が格納されているフォルダを指定
# # 画像データをAverage hashに変換
# def average_hash(target_file, size):
#     img = Image.open(target_file)   # Image.Openで画像ファイルをオープン
#     img = img.convert('L').resize((size, size), Image.ANTIALIAS) # グレースケール変換＆アンチエイリアス処理で圧縮
#     px = np.array(img.getdata()).reshape((size, size))  # 画素データを取得してリサイズ
#     avg = px.mean()  # 画素値の平均値を取得
#     px = 1 * (px > avg)   # 画素データ（px）で平均より大きい要素を1に、それ以外は0に変換
#     return px

# # 2つのAverageHash値間のハミング距離を求める 
# def hamming_dist(a, b):    
#     a = a.reshape(1, -1)  # 1次元に変換
#     b = b.reshape(1, -1)  # 1次元に変換
#     dist = (a != b).sum()  # 要素が異なる部分の合計値を計算
#     return dist

# target_dist = average_hash(target_file, size)
# # rate =2.0
# sim_hash_dict = {}
# for fname in wanna_imgs:
#     try:
#         dist = average_hash(fname, size)
#         diff = hamming_dist(target_dist, dist) / 256
#         # if diff < rate:
#     except:
#         diff = 100000
#     sim_hash_dict[fname[37:]] = diff
# print(sim_hash_dict)