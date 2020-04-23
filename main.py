import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired
import os
import json
from flask import jsonify
from random import shuffle
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexliceum_secret_key'
communityId = -1


class IdForm(FlaskForm):
    id = StringField("id", validators=[DataRequired()])
    submit = SubmitField("Find")


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/', methods=['GET', 'POST'])
def mainPage():
    form = IdForm()
    print(*form)
    if form.validate_on_submit():
        return redirect('/stat/' + form.id.data)
    return render_template('mainpage.html', title='vk statistics', form=form)


@app.route('/stat')
def red():
    return redirect('/')


@app.route('/test')
def test():
    return render_template("test.html")


@app.route('/stat/<id>', methods=['GET', 'POST'])
def stat(id):
    global communityId

    login, password = "89022602020", "Pleasedonttouchmyaccountthanks!"
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    #  print(id)
    try:
        communityId = int(id)
    except ValueError:
        communityId = vk.utils.resolveScreenName(screen_name=id)["object_id"]
    #print(communityId)

    community = vk.groups.getById(group_id=id)
    #  print(community)
    try:
        stats = vk.stats.get(group_id=communityId, interval="day", intervals_count=10)
    except vk_api.exceptions.ApiError:
        return render_template("error.html", title="error")
    print(communityId)
    print(stats)
    print(len(stats))

    activity = {}
    age = {}
    cities = {}

    for block in stats:
        for act in block["activity"]:
            if act not in activity:
                activity[act] = 0
            activity[act] += block["activity"][act]
        for ag in block["reach"]["age"]:
            if ag["value"] not in age:
                age[ag["value"]] = 0
            age[ag["value"]] += ag["count"]
        for city in block["reach"]["cities"]:
            if city["name"] not in cities:
                cities[city["name"]] = 0
            cities[city["name"]] += city["count"]

    sts = [activity, age, cities]

    indexes = [0, 1, 2]
    shuffle(indexes)
    t = indexes
    c = []
    for i in t:
        c.append(["purple", "green", "blue"][i])

    return render_template("stat.html", id=communityId, name=community[0]["name"], stats=sts, colors=c)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
