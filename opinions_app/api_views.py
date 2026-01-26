# what_to_watch/opinions_app/api_views.py

from flask import jsonify, request

from . import app, db
from .models import Opinion
from .views import random_opinion
from .error_handlers import InvalidAPIUsage

@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    opinion = Opinion.query.get(id)
    if opinion is None:
        # Тут код ответа нужно указать явным образом.
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    data = request.get_json()
    if (
        'text' in data and 
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        # При неуникальном значении поля text
        # вернуть сообщение об ошибке в формате JSON 
        # и статус-код 400.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion.query.get(id)
    # Тут код ответа нужно указать явным образом.
    if opinion is None:
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    db.session.commit()  
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get(id)
    if opinion is None:
        # Тут код ответа нужно указать явным образом.
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    db.session.delete(opinion)
    db.session.commit()
    # При удалении принято возвращать только код ответа 204.
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    # Запросить список объектов.
    opinions = Opinion.query.all()
    # Поочерёдно сериализовать каждый объект,
    # а потом все объекты поместить в список opinions_list.
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        # Выбросить собственное исключение.
        # Второй параметр (статус-код) в этом обработчике можно не передавать:
        # нужно вернуть код 400, а он и так возвращается по умолчанию.
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    if Opinion.query.filter_by(text=data['text']).first() is not None:
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201 

@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion = random_opinion()
    # Если мнение найдено (переменная opinion не равна None),
    # оно возвращается в виде JSON-объекта с кодом ответа 200 (OK).
    if opinion is not None:
        return jsonify({'opinion': opinion.to_dict()}), 200
    # Если мнение не найдено (opinion равен None), 
    # вызывается исключение InvalidAPIUsage с сообщением об ошибке 
    # и кодом ответа 404 (Not Found).
    raise InvalidAPIUsage('В базе данных нет мнений', 404) 