from flask import render_template, request, redirect
import time
from database import Photos
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
    photo = Photos.query.filter_by(tag=None).first()
    return render_template('show_photo.html', photo=photo)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
