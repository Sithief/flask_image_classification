from flask import render_template, request, redirect
import time
from database import Photos
import photos_updater
from __init__ import *


@app.route('/', methods=['GET'])
def index():
    tasks = Photos.query.order_by(Photos.id).all()
    return render_template('index.html', tasks=tasks)


@app.route('/add_tag/<int:photo_id>', methods=["POST"])
def add_tag(photo_id):
    photo = Photos.query.get_or_404(photo_id)
    photo.tag = request.form['tag']
    photo.update_time = int(time.time())
    try:
        db.session.commit()
        return redirect('/show_photo')
    except:
        return 'error'


@app.route('/register')
def register():
    client_id = CONF.get("VK", "client_id")
    scope = CONF.get("VK", "scope")
    uri = CONF.get("VK", "uri")
    url = f'https://oauth.vk.com/authorize?client_id={client_id}&redirect_uri={uri}&scope={scope}' \
          f'&display=page&response_type=token&revoke=1'
    return redirect(url)


@app.route('/confirm_register')
def confirm_register():
    access_token = request.args.get('access_token')
    if not access_token:
        return render_template('register.html')
    else:
        return access_token


@app.route('/delete/<int:photo_id>')
def delete(photo_id):
    task = Photos.query.get_or_404(photo_id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except:
        return 'error'


@app.route('/show_photo')
def show_photo():
    photo_id = request.args.get('photo_id')
    if photo_id:
        photo = Photos.query.get_or_404(photo_id)
    else:
        photo = Photos.query.filter_by(tag=None).first()
        if photo is None:
            token = CONF.get('VK', 'token', fallback=None)
            if token:
                vk_api = photos_updater.VkApi(token)
                new_data = photos_updater.get_new_data(vk_api)
                print('new_data', new_data)
                return redirect('/show_photo')
    return render_template('show_photo.html', photo=photo)


@app.route('/gallery')
def gallery():
    tags = db.session.query(func.count(Photos.tag).label('count'), Photos.tag).group_by(Photos.tag).all()
    current_tag = request.args.get('tag')
    if current_tag:
        photos = Photos.query.filter(Photos.update_time > 0, Photos.tag == current_tag)\
            .order_by(Photos.update_time.desc())\
            .limit(100).all()
    else:
        photos = Photos.query.filter(Photos.update_time > 0) \
            .order_by(Photos.update_time.desc()) \
            .limit(100).all()

    # for tag in tags:
    #     print(tag.tag, tag.count)
    return render_template('gallery.html', tag_list=tags, photos=photos)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
