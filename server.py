import logging
from sense_hat import SenseHat
from flask import Flask, render_template
from flask_socketio import SocketIO
#from fake_sense_hat import SenseHat

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

_log = logging.getLogger(__name__)
sense = SenseHat()

pixels_matrix = [[[255, 255, 255] for _ in range(8)] for _ in range(8)] 

@app.route('/')
def index():
    _log.info("route /")

    #sense.show_message("Hello world!")
    return render_template('index.html')

def decode(s):
    r = int(s[1] * 2, 16)
    g = int(s[2] * 2, 16)
    b = int(s[3] * 2, 16)
    
    return [r, g, b]

@socketio.on('message')
def handle_message(message):
    print('received message: {}'.format(message))

    for key, color in message.items():
        row = int(key[1])
        col = int(key[3])

        rgb = decode(color)
        print(rgb)

        pixels_matrix[row][col] = rgb
        _log.info(pixels_matrix)

    sense_list = []
    for row in pixels_matrix:
        for element in row:
            sense_list.append(element)
    sense.set_pixels(sense_list)

    socketio.emit('update', message, broadcast=True)


def pixel2msg():
    msg=dict()
    for row in range(8):
        for col in range(8):
            key = 'r{}c{}'.format(row, col)
            r, g, b = pixels_matrix[row][col]
            # "#FFF"
            color = "#" + ("%02X" % r)[0] + ("%02X" % g)[0] + ("%02X" % b)[0]
            msg[key] = color
    return msg




@socketio.on('connect')
def initialize():

    message = pixel2msg()
    socketio.emit("update",message)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    socketio.run(app, host='0.0.0.0')
