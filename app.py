from flask import Flask, request, url_for
from werkzeug.utils import secure_filename

from random import choice
from string import ascii_letters
from os import listdir

from cv2 import imread, CascadeClassifier, COLOR_BGR2RGB, cvtColor
from cv2.data import haarcascades

from PIL.Image import fromarray, open
from PIL.ImageDraw import Draw

app = Flask(__name__, static_folder='cache')


def gen_filename():
    while True:
        a = ''.join([choice(ascii_letters) for _ in range(16)]) + '.png'
        if a not in listdir():
            return secure_filename(a)


@app.route('/gen', methods=['POST'])
def generate():
    try:
        face = request.files['replace']
        facename = f'cache/{gen_filename()}'

        image = request.files['image']
        imagename = f'cache/{gen_filename()}'
        if face.filename.split('.')[1] not in ['png', 'jpg', 'jpeg'] or image.filename.split('.')[1] not in ['png', 'jpg', 'jpeg']:
            return {'message': 'file type must be one of "png", "jpg", "jpeg"'}, 400

        face.save(facename)
        image.save(imagename)

        scale = float(request.form['scale']) if 'scale' in request.form else 1.3

        cv2_image = cvtColor(imread(imagename), COLOR_BGR2RGB)
        pillow_image = fromarray(cv2_image)

        faces = CascadeClassifier(haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(cv2_image, scaleFactor=scale, minNeighbors=3, minSize=(30, 30))
        if not len(faces):
            return {'message': 'Face not found'}, 412

        for (x, y, w, h) in faces:
            pillow_image.paste(open(facename).resize((w, h)), (x, y))

        name = f'cache/res/{gen_filename()}'
        pillow_image.save(name)

        return {'filename': name, 'route': url_for('static', filename=f'res/{name[10:]}')}
    except:
        return {'error': 'Wa'}, 500


if __name__ == '__main__':
    app.run(debug=True)
