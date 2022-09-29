from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField

from web_calendar_maker import Chumon, Data

# reference
# ファイルのI/O
# https://tanuhack.com/flask-client2server/#i-7
# https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/patterns/fileuploads.html

upload_folder = '../app/static/files'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = upload_folder

class undesire_form(FlaskForm):
    # undesired = SelectMultipleField('いらないメニューを選んでね', choices=[('a', 'aaaaaaaaaaa'), ('b', 'bbbbbb')])
    # undesired = SelectMultipleField('いらないメニューを選んでね', source=[111111,222222222,33333])
    undesired = SelectMultipleField()

@app.route('/', methods=['GET', 'POST'])
def input_page():
    return render_template('input.html')

@app.route('/undesired', methods=['GET', 'POST'])
def undesired():
    # 読み込んだエクセルをstaticディレクトリに保存しておく必要がある
    # あなたは誰？
    file = request.files['input_file']
    file.save(app.config['UPLOAD_FOLDER'] + '/input.xlsx')
    # data = Data(request.files.get('input_file'))    
    # menus = list(data.raw_df['メニュー'].values)
    # choices = [(menu, menu) for menu in menus]
    # undes_form = undesire_form()
    # undes_form.undesired.choices = choices 
    
    return render_template('undesired.html', undes_form=undes_form)
    # return (request.args.get('input_file'))

@app.route('/process', methods=['GET', 'POST'])
def process_data_by_web_calendar_maker():
    data = Data(request.form.get('input_file'))
    data.extract_data()
    chumon = Chumon(10, data)

    chumon.make_calendar()
    chumon.make_daily_order()
    chumon.daily_orders

# @app.route('/test', methods=['GET', 'POST'])
# def test_page():
#     # data = Data()


#     form = undesire_form()
#     return render_template('test.html', form=form)

# @app.route('/test_print', methods = ['GET', 'POST'])
# def test_print():
#     file = request.form.get('input_file')
#     print(type(file))
#     return redirect(url_for('input_page'))

# if __name__ == 'main':
app.run(debug=True)
