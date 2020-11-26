from functools import wraps
from typing import Tuple, Optional

import requests
from flask import render_template, redirect, url_for, request, make_response
from werkzeug.wrappers import BaseResponse

from resources import create_app, config
from resources.forms import LoginForm, RegistrationForm, DBForm

app = create_app(mode=config.Development)


def is_logged_in():
    """Checks if user is logged in if `username`
    is passed check if specified user is logged in
    username can be a list"""
    if "token" not in request.cookies:
        return False
    data = {'token': request.cookies.get('token')}
    app.logger.debug(data)

    req = requests.get("http://auth:5050/api/auth", json=data)
    app.logger.debug(req.text)

    return req.status_code == 200


def login_required(function=None):
    """Decorate views to require login
    @login_required
    @login_required()
    """

    if function and not callable(function):
        raise ValueError(
            'Decorator receives only named arguments, '
            'try login_required(username="foo")'
        )

    def dispatch(fun, *args, **kwargs):
        if is_logged_in():
            return fun(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.path))

    if function:
        @wraps(function)
        def simple_decorator(*args, **kwargs):
            """This is for when decorator is @login_required"""
            return dispatch(function, *args, **kwargs)

        return simple_decorator

    def decorator(f):
        """This is for when decorator is @login_required(...)"""

        @wraps(f)
        def wrap(*args, **kwargs):
            return dispatch(f, *args, **kwargs)

        return wrap

    return decorator


def login_checker(user: dict) -> Tuple[Optional[str], int]:
    email: str = user.get('email')
    password: str = user.get('password')

    data = {'email': email, 'password': password}
    req = requests.post("http://auth:5050/api/auth", json=data)
    app.logger.debug(req.text)
    if req.status_code == 200:
        app.logger.debug("Login successful")
        return req.json()['token'], 200
    return None, 403


def regisr(user: dict) -> Tuple[Optional[str], int]:
    email: str = user.get('email')
    password: str = user.get('password')

    data = {'email': email, 'password': password}
    req = requests.post("http://auth:5050/api/user", json=data)
    app.logger.debug(req.text)
    if req.status_code == 200:
        app.logger.debug("Registration successful")
        return req.json()['token'], 200
    return None, 401


@app.route('/login', methods=['GET', 'POST'])
def login():
    destiny = request.args.get(
        'next',
        default=request.form.get(
            'next',
            default='/'
        )
    )
    form = LoginForm(meta={'csrf': False})
    ret_code = 200
    if form.validate_on_submit():
        app.logger.debug(form.data)
        token, ret_code = login_checker(form.data)
        if ret_code == 200:
            res: BaseResponse = make_response(redirect(destiny))
            app.logger.debug(res.headers)
            res.set_cookie('token', token, max_age=60 * 60 * 24 * 365 * 2)
            app.logger.debug(res.headers)

            return res
    return render_template('auth/login.html', form=form, next=destiny), ret_code

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    destiny = request.args.get(
        'next',
        default=request.form.get(
            'next',
            default='/'
        )
    )
    form = RegistrationForm(meta={'csrf': False})
    ret_code = 200
    if form.validate_on_submit():
        app.logger.debug(form.data)
        token, ret_code = regisr(form.data)
        if ret_code == 200:
            res: BaseResponse = make_response(redirect(destiny))
            app.logger.debug(res.headers)
            res.set_cookie('token', token, max_age=60 * 60 * 24 * 365 * 2)
            app.logger.debug(res.headers)

            return res
    return render_template('auth/registration.html', form=form, next=destiny), ret_code

@app.route('/logout', methods=['GET'])
def logout():
    res: BaseResponse = make_response(redirect("/login"))
    app.logger.debug(res.headers)
    res.set_cookie('token', '', max_age=0)
    app.logger.debug(res.headers)

    return res

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = DBForm(meta={'csrf': False})
    if form.validate_on_submit():
        data = {"text": form.text.data, "token": request.cookies.get("token")}
        req = requests.post("http://auth:5050/api/db", json=data)
        if req.status_code != 200:
            return redirect(url_for('login', next=request.path))
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
