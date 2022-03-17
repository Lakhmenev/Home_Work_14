import sqlite3
# from pprint import pprint as pp

DATABASE = "db/netflix.db"
DB_NAME = 'netflix'


def get_db_result(sqlite_query):
    """
    Функция работы  с  БД
    :param sqlite_query: SQL запрос к  БД
    :return: Результат выполнения  запроса
    """
    con = sqlite3.connect(DATABASE)
    try:
        cursor = con.cursor()
        try:
            cursor.execute(sqlite_query)
            executed_query = cursor.fetchall()
            if executed_query is not None:
                return executed_query
            return None
        finally:
            cursor.close()
    finally:
        con.close()


def get_find_title_last_film(find_title):
    """
    Функция возвращает самый свежий фильм из найденных по названию
    :param find_title: искомое название фильма
    :return: переформатированный словарь в формате json
    """
    sql_query = f'SELECT title, country, release_year, listed_in, description FROM {DB_NAME} ' \
                f'WHERE title LIKE "%{find_title}%" ' \
                f'ORDER BY release_year DESC'
    result = get_db_result(sql_query)

    if result is not None:
        last_film = {'title': result[0][0], 'country': result[0][1], 'release_year': result[0][2],
                     'genre': result[0][3], 'description': result[0][4]}
        return last_film
    return None


def search_by_range_of_release_years(begin_year, end_year):
    """
    Функция получает список фильмов выпущенных в межгодовой период включительно
    :param begin_year: начальный год
    :param end_year: конечный год
    :return: список фильмов в формате json
    """
    sql_query = f'SELECT title, release_year FROM {DB_NAME} ' \
                f'WHERE release_year ' \
                f'BETWEEN {begin_year} AND {end_year} ' \
                f'ORDER BY release_year ' \
                f'LIMIT 100'
    result = get_db_result(sql_query)
    if result is not None:
        list_films = []
        for item in range(len(result)):
            dict_film = {'title': result[item][0], 'release_year': result[item][1]}
            list_films.append(dict_film)
        return list_films
    return None


def search_by_rating(rating_list):
    """
    Функция возвращает список фильмов в зависимости от заданного рейтинга
    :param rating_list: список рейтингов  для  фильтра
    :return: Список фильмов в формате json
    """
    # Подготовим строку фильтра  для SQL запроса
    group_rating = ''
    for rating in rating_list:
        group_rating = group_rating + "'" + rating + "',"

    sql_query = f'SELECT title, rating, description FROM {DB_NAME} ' \
                f'WHERE rating IN ({group_rating[0:-1]})'

    result = get_db_result(sql_query)
    if result is not None:
        list_films = []
        for item in range(len(result)):
            dict_film = {'title': result[item][0], 'rating': result[item][1], 'description': result[item][2]}
            list_films.append(dict_film)
        return list_films
    return None


def search_last_films_by_genre(genre):
    """
    Функция получает список из 10 последних фильмов заданного жандра
    :param genre: жандр
    :return: Список фильмов в формате json
    """
    sql_query = f'SELECT title, description FROM {DB_NAME} ' \
                f'WHERE listed_in LIKE "%{genre}%" ' \
                f'ORDER BY release_year DESC ' \
                f'LIMIT 10'

    result = get_db_result(sql_query)
    if result is not None:
        list_films = []
        for item in range(len(result)):
            dict_film = {'title': result[item][0], 'description': result[item][1]}
            list_films.append(dict_film)
        return list_films
    return None


def search_of_actors_for_couple_of_actors(one_actor, two_actor):
    """
    Функция получает список актёров которые более 2 раз снимались вместе с двумя  заданными актёрами
    :param one_actor: первый актёр
    :param two_actor: второй актёр
    :return: список актёров  где они участвовали в фильме вместе  более 2 раз
    """
    # Получим фильмы в которых играет эта пара актёров
    sql_query = f'SELECT {DB_NAME}.cast FROM {DB_NAME} ' \
                f'WHERE {DB_NAME}.cast LIKE "%{one_actor}%" ' \
                f'AND {DB_NAME}.cast LIKE "%{two_actor}%"'

    print(sql_query)
    # Составим уникальных список всех актёров которые играли вместе с этой парой
    result = get_db_result(sql_query)
    if result is not None:
        list_actors = []
        list_actors_unique = []
        for item in result:
            list_actors.append(*item)

        # Получим уникальный список
        for item in list_actors:
            list_actors_unique = list_actors_unique + item.split(', ')
        list_actors_unique = list(set(list_actors_unique))

        # Удаляем из списка первого и второго актёра
        list_actors_unique.remove(one_actor)
        list_actors_unique.remove(two_actor)

        # Начинаем проверять сколько раз каждый актёр из уникального списка сыграл с парой наших актёров
        list_actors = []
        for three_actor in list_actors_unique:
            sql_query = f'SELECT count() FROM {DB_NAME} ' \
                        f'WHERE {DB_NAME}.cast LIKE "%{one_actor}%" ' \
                        f'AND {DB_NAME}.cast LIKE "%{two_actor}%" ' \
                        f'AND {DB_NAME}.cast LIKE "%{three_actor}%" '

            result = get_db_result(sql_query)
            if result[0][0] > 2:
                list_actors.append(three_actor)
        return list_actors
    return None


def search_films_by_type_release_years_genre(type_film=None, release_years=None, genre=None):
    """
    Функция по одному, двум или трем независимым фильтрам получает список фильмов удовлетворяющих фильтру
    :param type_film: фильтр по типу
    :param release_years: фильтр по году выхода на экраны
    :param genre: фильтр по жанру
    :return: список удовлетворяющий  условиям фильтра в формате json
    """
    flag_is_present = False
    sql_query = f'SELECT title, description FROM {DB_NAME} '

    # Обработка  если какой то из параметров  не указан
    if type_film is not None or release_years is not None or genre is not None:
        sql_query = sql_query + f'WHERE '

        if type_film is not None:
            sql_query = sql_query + f'type="{type_film}" '
            flag_is_present = True

        if flag_is_present and release_years is not None:
            sql_query = sql_query + f'AND release_year={release_years} '
        elif not flag_is_present and release_years is not None:
            sql_query = sql_query + f'release_year={release_years} '
            flag_is_present = True

        if flag_is_present and genre is not None:
            sql_query = sql_query + f'AND listed_in LIKE "%{genre}%" '
        elif not flag_is_present and genre is not None:
            sql_query = sql_query + f'listed_in LIKE "%{genre}%"'

    result = get_db_result(sql_query)
    # Переведём в json
    list_films = []
    for item in range(len(result)):
        dict_film = {'title': result[item][0], 'description': result[item][1]}
        list_films.append(dict_film)
    return list_films


# pp(get_find_title_last_film('marvel'))
# pp(search_by_range_of_release_years(2000, 2001))
# pp(search_by_rating(GROUP_FAMILY_VIEWING))
# pp(search_last_films_by_genre('Dramas'))
# pp(search_of_actors_for_couple_of_actors('Jack Black', 'Dustin Hoffman'))
# pp(search_films_by_type_release_years_genre(type_film='TV Show',release_years=2020, genre='Dramas'))
# pp(search_films_by_type_release_years_genre(release_years=2020, genre='Dramas'))
# pp(search_films_by_type_release_years_genre(type_film='TV Show', genre='Dramas'))
# pp(search_films_by_type_release_years_genre(genre='Dramas'))
# pp(search_films_by_type_release_years_genre(type_film='TV Show', release_years=2002, genre='Dramas'))
