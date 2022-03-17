from flask import Flask, jsonify
import utils

# Группы фильмов по рейтингу
# Для детей
GROUP_CHILDREN_VIEWING = ['G']
# Для семейного просмтора
GROUP_FAMILY_VIEWING = ['G', 'PG', 'PG-13']
# Для взрослых
GROUP_ADULT_VIEWING = ['R', 'NC-17']


app = Flask(__name__)


@app.route('/movie/<title>')
def movie_last(title):
    result = utils.get_find_title_last_film(title)
    return jsonify(result)


@app.route('/movie/<begin_year>to<end_year>')
def movie_for_the_period(begin_year, end_year):
    result = utils.search_by_range_of_release_years(begin_year, end_year)
    return jsonify(result)


@app.route('/rating/<group_rating>')
def movie_rating(group_rating):
    rating_list = []
    if group_rating == 'children':
        rating_list = GROUP_CHILDREN_VIEWING
    elif group_rating == 'family':
        rating_list = GROUP_FAMILY_VIEWING
    elif group_rating == 'adult':
        rating_list = GROUP_ADULT_VIEWING

    result = utils.search_by_rating(rating_list)
    return jsonify(result)


@app.route('/genre/<genre>')
def movie_genre(genre):
    result = utils.search_last_films_by_genre(genre)
    return jsonify(result)


if __name__ == '__main__':
    app.debug = True
    app.run(host="127.0.0.1", port=5000)
