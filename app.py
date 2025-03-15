from flask import Flask, render_template, request, redirect, url_for, flash
from calculator import proceed_input_data, check_for_correcting_need_by_id
import database as db

app = Flask(__name__)
app.secret_key = "idk_lol"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if request.method == 'POST':
        meter_id = request.form.get('meter_id')
        day_value = float(request.form.get('day_value'))
        night_value = float(request.form.get('night_value'))
        confirm = request.form.get("confirm")

        if not confirm and not check_for_correcting_need_by_id(meter_id, day_value, night_value):
            flash("Ви ввели менші значення, ніж попередні! Натисніть 'Підтвердити', якщо впевнені.",
                  "warning")
            return render_template('input.html', meter_id=meter_id, day_value=day_value,
                                   night_value=night_value, confirm=True)

        proceed_input_data(meter_id, day_value, night_value)
        flash("Дані успішно додано!", "success")
        return redirect(url_for('history_page'))

    return render_template('input.html', confirm=False)


@app.route('/history')
def history_page():
    try:
        history = db.get_history()
    except ValueError:
        history = []
    return render_template('history.html', history=history)


if __name__ == '__main__':
    app.run(debug=True)
