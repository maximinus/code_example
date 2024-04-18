from flask import Flask, jsonify, render_template
from database import get_existing_sensors, get_last_data

app = Flask(__name__,
            static_url_path='',
            static_folder='')


@app.route('/')
def home():
    template_data = {'sensors': get_existing_sensors(),
                     'title': 'Simple Sensor Example'}
    return render_template('index.html', **template_data)


@app.route('/get_sensor_data/<sensor_name>', methods=['GET'])
def get_data(sensor_name):
    print(sensor_name)
    full_data = get_last_data(sensor_name.replace('_', ' '))
    return jsonify({'data': full_data})


if __name__ == "__main__":
    app.run(debug=True)
