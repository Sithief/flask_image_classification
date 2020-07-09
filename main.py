from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text(200), nullable=False)
    tag = db.Column(db.Text(200))
    update_time = db.Column(db.Integer)

    def __repr__(self):
        return f"<Photo {self.id}>"


@app.route('/', methods=['GET'])
def index():
    tasks = Photos.query.order_by(Photos.id).all()
    return render_template('index.html', tasks=tasks)


@app.route('/add_tag/<int:photo_id>', methods=["POST"])
def add_tag(photo_id):
    photo = Photos.query.get_or_404(photo_id)
    photo.tag = request.form['tag']

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
