from flask import Flask, render_template ,request, session, redirect, url_for, send_from_directory, jsonify
import os
import time
from library_dir.func_box import self_func
import functools
import json
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./static/images/input_image"

# urlリダイレクト用
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def add_upper_path(x,upper_):
    return upper_ + x

def add_natural_path(x):
    return "images/image_storage/natural_box/" + x

# セッション維持用
# ↓触るな!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
app.secret_key = "TomorrowandtomorrowandtomorrowCreepsinthispettypacefromdaytodayTothelastsyllableofrecordedtimeAndallouryesterdayshavelightedfoolsThewaytodustydeathOutoutbriefcandleLifesbutawalkingshadowapoorplayer"

# 自前関数
lib = self_func()

good_bad_id_box = 0

# メインページ
@app.route("/", methods=['GET','POST'])
def index():
    input_img_box = os.listdir("static/images/input_image")
    for i in input_img_box:
        os.remove("static/images/input_image/"+i)
    print("hi!")
    if "input_clothes" in session:
        session.pop("input_clothes",None)
    if "input_clothes" not in session:
        print("入ってない")
    else:
        print("入ってる")
    return render_template("index.html")

@app.route("/select_clothes", methods=['GET','POST'])
def gopp():
    box_name = ["./static/images/output_image/tops_box/","./static/images/output_image/bottoms_box/"]
    for name_ in box_name:
        box_files = os.listdir(name_)
        for i in box_files:
            os.remove(name_+i)
    if "input_clothes" in session and ("input_clothes" not in request.form):
        upload_img = session["input_clothes"]
    elif ("input_clothes" in request.files):
        input_path = request.files["input_clothes"]
        session["input_clothes"] = os.path.join(app.config['UPLOAD_FOLDER'], input_path.filename)
        upload_img = session["input_clothes"]
        input_path.save(upload_img)
    else:
        return redirect(url_for('index'))
    oh_its_fucking_img = lib.remove_back(upload_img)
    oh_its_fucking_img.save("./static/images/only_image/only_human.png")
    lib.cutting_wear()
    tops_files = os.listdir("./static/images/output_image/tops_box")
    bottoms_files = os.listdir("./static/images/output_image/bottoms_box")
    tops_files = list(map(functools.partial(add_upper_path, upper_="images/output_image/tops_box/"), tops_files))
    bottoms_files = list(map(functools.partial(add_upper_path, upper_="images/output_image/bottoms_box/"), bottoms_files))
    print(tops_files,bottoms_files)
    tops_num = len(tops_files)
    bottoms_num = len(bottoms_files)
    all_files = os.listdir("./static/images/output_image/tops_box") + os.listdir("./static/images/output_image/bottoms_box")

    
    return render_template(
        "select_clothes.html",
        tops_files=tops_files,
        bottoms_files=bottoms_files,
        tops_num=tops_num,
        bottoms_num=bottoms_num,
        all_files=all_files)

@app.route("/show_result", methods=['GET','POST'])
def show_result():
    if "select_clothes" in session and ("select_clothes" not in request.form):
        select_clothes = session["select_clothes"]
        which = session["which"]
        concept = session["concept"]
    else:
        select_clothes = request.form["select_clothes"]
        which = request.form["select_which"]
        concept = request.form["select_concept"]
        session["select_clothes"] = select_clothes
        session["which"] = which
        session["concept"] = concept
    tops_files = os.listdir("./static/images/output_image/tops_box")
    bottoms_files = os.listdir("./static/images/output_image/bottoms_box")
    if select_clothes in tops_files:
        select_img_path = "./static/images/output_image/tops_box/"+select_clothes
    elif select_clothes in bottoms_files:
        select_img_path = "./static/images/output_image/bottoms_box/"+select_clothes
    sim_list = lib.get_sim_name(which,concept,select_img_path)
    sim_path_list = list(map(add_natural_path,sim_list))
    return render_template(
        "show_result.html",
        sim_list=sim_list,
        sim_path_list=sim_path_list,
        cout_num = len(sim_list)
    )

@app.route("/show_detail", methods=['GET','POST'])
def show_detail():
    if "detail_img" in session and ("detail_image" not in request.form):
        detail_img = session["detail_img"]
    else:
        detail_img = request.form["detail_image"]
        session["detail_img"] = detail_img
    detail_img_path = "images/image_storage/natural_box/"+detail_img
    detail_data = lib.get_detail(detail_img[:-4])
    detail_dict = {
        "name":detail_data[1],
        "category":detail_data[3],
        "material":detail_data[4],
        "concept":detail_data[5],
        "maker":detail_data[6],
        "price":detail_data[7],
        "ex_text":detail_data[8],
        "url":detail_data[9]
    }
    good_bad = lib.get_like(detail_data[0])
    print(good_bad)
    session["now_id"] = detail_data[0]
    print(detail_img,detail_dict)
    return render_template(
        "show_detail.html",
        detail_img_path = detail_img_path,
        item_name = detail_dict["name"],
        item_category = detail_dict["category"],
        item_material = detail_dict["material"],
        item_concept = detail_dict["concept"],
        item_maker = detail_dict["maker"],
        item_price = detail_dict["price"],
        item_ex_text = detail_dict["ex_text"],
        item_url = detail_dict["url"],
        good = good_bad[0]-3,
        bad = good_bad[1]-3,
        id_ = detail_data[0]
    )

@app.route("/good_def", methods=['GET','POST'])
def good_def():
    print("good",session["now_id"])
    res = lib.add_like(session["now_id"],"good")
    print(res)
    return jsonify({'message': 'success post'}), 500

@app.route("/bad_def", methods=['GET','POST'])
def bad_def():
    print("bad",session["now_id"])
    res = lib.add_like(session["now_id"],"bad")
    print(res)
    return jsonify({'message': 'success post'}), 500