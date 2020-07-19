from flask import render_template, request, redirect, url_for, Response
from werkzeug.wsgi import FileWrapper
from sqlalchemy.sql import func
import time
import os
import io
from database import Photos
import photos_updater
import downloader
from __init__ import *


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


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
        photo = Photos.query.filter_by(tag=None).order_by(func.random()).first()
        while photo is None:
            token = CONF.get('VK', 'token', fallback=None)
            if token:
                vk_api = photos_updater.VkApi(token)
                new_data = photos_updater.get_new_data(vk_api)
                print('new_data', new_data)
            else:
                return 'no vk_api token'
            photo = Photos.query.filter_by(tag=None).order_by(func.random()).first()
        redirect_url = url_for('show_photo', photo_id=photo.id)
        return redirect(redirect_url)
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

    return render_template('gallery.html', tag_list=tags, photos=photos)


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == "POST":
        dir_name = os.path.join(CONF.get('SERVER', 'files_dir'), hex(int(time.time()))[2:])
        if request.form.get('img_height') and request.form.get('img_width'):
            img_size = (min(640, int(request.form.get('img_height'))),
                        min(640, int(request.form.get('img_width'))))
            max_count = min(5000, int(request.form.get('max_count', 100)))
        else:
            img_size = None
            max_count = min(1000, int(request.form.get('max_count', 100)))
        tag = request.form.get('tag', 100)

        photos = Photos.query.filter(Photos.tag == tag)\
            .order_by(Photos.update_time.desc())\
            .limit(max_count).all()
        urls = [ph.url for ph in photos]
        downloader.main(urls, dir_name, img_size)
        zip_file = downloader.zipdir(dir_name)

        return_data = io.BytesIO()
        with open(zip_file, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)
        os.remove(zip_file)
        wrapped_data = FileWrapper(return_data)
        return Response(wrapped_data, mimetype="application/zip", direct_passthrough=True)
    else:
        tags = db.session.query(func.count(Photos.tag).label('count'), Photos.tag).group_by(Photos.tag).all()
        return render_template('download.html', tag_list=tags)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
