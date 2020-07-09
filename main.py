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
