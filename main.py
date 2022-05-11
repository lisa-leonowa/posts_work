from flask import Flask, render_template, make_response, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect
import datetime
import pandas


dict_result = {}  # хранится информации о запрашиваемых файлах
file_df = pandas.read_csv('posts.csv')  # чтение файла с данными
app = Flask(__name__)  # создание приложения
app.config['SECRET_KEY'] = 'posts'


class Search(FlaskForm):  # форма для ввода запроса
    zapros_search = StringField('Введите свой запрос', validators=[DataRequired()])
    submit = SubmitField('Найти')


def main():
    app.run(port=4008, host='192.168.0.100')


@app.route("/delete/<int:id_posts>")  # удаление информации
def delete(id_posts):
    global file_df
    file_df = file_df.drop(labels=[id_posts], axis=0)  # удаление по id
    file_df.to_csv('posts.csv')  # сохранение в cvs
    return redirect('/')  # переход на форму для ввода запроса


@app.route("/res", methods=['GET', 'POST'])  # отображение результатов
def res():
    global dict_result
    list_keys = list(dict_result.keys())
    # сортировка словаря по дате создания, с учетом времени создания
    list_keys = sorted(list_keys, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'),
                       reverse=False)
    counter = 1  # номер документа
    otv = []  # список всей информации первых 20 подходящих элементов
    list_keys = list_keys[0:20]
    for i in list_keys:  # информации о первых 20 документах
        vr = [counter, dict_result[i]['id'], dict_result[i]['rubrics'], dict_result[i]['text'], i]
        otv.append(vr)
        counter += 1
    return render_template("res.html", title='Результат', otv=otv)  # переход на форму отображения результатов


@app.route("/", methods=['GET', 'POST'])  # форма обработки запроса
def index():
    global file_df
    form = Search()
    if form.validate_on_submit() or form.submit.data:  # если форма отправлена
        global dict_result
        dict_result = {}
        zapros = form.zapros_search.data  # запрос пользователя
        file_df = pandas.read_csv('posts.csv')   # открытие csv как фрейм данных
        for i in range(len(file_df)):
            if zapros.lower() in file_df['text'][i].lower():  # поиск по столбцу text
                vr = {}
                vr['text'] = file_df['text'][i]
                vr['rubrics'] = file_df['rubrics'][i]
                vr['id'] = i
                dict_result[file_df['created_date'][i]] = vr
        if dict_result:  # если нашелся хотя бы 1 документ - переход на форму отображения результатов
            return redirect('/res')
    return render_template("base.html", title='Поиск по текстам документов', form=form)  # переход на форму обработки запроса


@app.errorhandler(404)  # обработка 404 ошибки
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)   # обработка 500 ошибки
def internal_error(error):
    return "500 error - Server error"


if __name__ == '__main__':
    main()
