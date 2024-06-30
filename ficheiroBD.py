import random
import string

import flask
import logging
import psycopg2
import jwt
from functools import wraps
import time

#Eliminar morada_idmorada

app = flask.Flask(__name__)

secretKey = "124j1d012kbwefhwbe"

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

def db_connection():
    db = psycopg2.connect(
        user='projectBD',
        password='postgres',
        host='127.0.0.1',
        port='5432',
        database='projetoBD'
    )
    return db

def tokenValidation(temp):
    @wraps(temp)
    def aux(*args, **kwargs):
        if 'Token' not in flask.request.headers:
            response = {'status': StatusCodes["api_error"], 'results': 'Token not passed'}
            return flask.jsonify(response)
        conn = db_connection()
        cur = conn.cursor()
        try:
            found = 0
            userToken = flask.request.headers['Token']
            data = jwt.decode(userToken, secretKey, ['HS256'])
            if found == 0:
                statements = f'SELECT * FROM consumidor WHERE idpessoa = \'{data["userID"]}\''
                cur.execute(statements)
                user = cur.fetchall()
                if len(user) > 0:
                    data['role'] = 0
                    found = 1
            if found == 0:
                statements = f'SELECT * FROM artista WHERE idlogin = \'{data["userID"]}\''
                cur.execute(statements)
                user = cur.fetchall()
                if len(user) > 0:
                    data['role'] = 1
                    found = 1
            if found == 0:
                statements = f'SELECT * FROM administrador WHERE login_id = \'{data["userID"]}\''
                cur.execute(statements)
                user = cur.fetchall()
                if len(user) > 0:
                    data['role'] = 2
                    found = 1
            if found == 0:
                conn.close()
                response = {'status': StatusCodes["server_error"], 'results': 'Invalid Token'}
                return flask.jsonify(response)
        except:
            response = {'status': StatusCodes["server_error"], 'results': 'Invalid Token'}
            return flask.jsonify(response)
        return temp(data['userID'], data['role'], *args, **kwargs)
    return aux

@app.route('/user/', methods=['POST'])
def createUser():
    logger.info('POST /user')
    payload = flask.request.get_json()
    if 'username' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'username is null'}
        return flask.jsonify(response)
    if 'password' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'password is null'}
        return flask.jsonify(response)
    if 'email' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'email is null'}
        return flask.jsonify(response)
    if 'nome' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'nome is null'}
        return flask.jsonify(response)
    if 'morada' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'morada is null'}
        return flask.jsonify(response)
    if 'telefone' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'telefone is null'}
        return flask.jsonify(response)
    if 'codigopostal' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'codigopostal is null'}
        return flask.jsonify(response)
    if 'nomerua' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'nomerua is null'}
        return flask.jsonify(response)
    if 'pais' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'pais is null'}
        return flask.jsonify(response)
    if 'cidade' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'cidade is null'}
        return flask.jsonify(response)
    if 'nomeartista' in payload:
        if 'ideditora' not in payload:
            response = {'status': StatusCodes["api_error"], 'results': 'ideditora is null'}
            return flask.jsonify(response)
        if 'adminID' not in payload:
            response = {'status': StatusCodes["api_error"], 'results': 'adminID is null'}
            return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO login(email, password, username) values (%s,%s,%s) RETURNING id'
        values = (payload["email"], payload["password"], payload["username"])
        cur.execute(statements, values)
        loginID = cur.fetchone()[0]
        statements = 'INSERT INTO pessoa(nome, morada, telefone, codigopostal, nomerua, pais, cidade, datacriacao, login_id) values (%s,%s,%s,%s,%s,%s,%s,NOW(),%s)'
        values = (payload["nome"], payload["morada"], payload["telefone"],payload["codigopostal"], payload["nomerua"], payload["pais"], payload["cidade"], loginID)
        cur.execute(statements, values)
        if 'nomeartista' in payload:
            statements = f'SELECT * FROM administrador WHERE {payload["adminID"]} = login_id'
            cur.execute(statements)
            if len(cur.fetchall()) == 0:
                response = {'status': StatusCodes["api_error"], 'results': 'adminID is invalid'}
                return flask.jsonify(response)
            statements = 'INSERT INTO artista(nomeartista, ideditora, idlogin) values (%s,%s,%s)'
            values = (payload["nomeartista"], payload["ideditora"], loginID)
            cur.execute(statements, values)
        else:
            statements = 'INSERT INTO consumidor(idpessoa, dataPremium) values (%s, NOW() - \'1 month\')'
            values = (loginID, )
            cur.execute(statements, values)
        logger.debug('POST /user ')
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': loginID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/user/', methods=['PUT'])
def loginUser():
    logger.info('PUT /user')
    payload = flask.request.get_json()
    if 'username' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'username is null'}
        return flask.jsonify(response)
    if 'password' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'password is null'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()

    try:
        statements = f'SELECT id, username, password FROM login WHERE username = \'{payload["username"]}\' AND password = \'{payload["password"]}\''
        cur.execute(statements)
        user = cur.fetchall()
        if len(user) == 0:
            response = {'status': StatusCodes["api_error"], 'results': 'user not found'}
            return flask.jsonify(response)
        token = jwt.encode({"userID":user[0][0]}, key = secretKey, algorithm = 'HS256')
        response = {'status': StatusCodes['success'], 'results': token}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/song/', methods=['POST'])
@tokenValidation
def addSong(userID, role):
    logger.info('POST /song')
    payload = flask.request.get_json()
    if 'titulo' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'titulo is null'}
        return flask.jsonify(response)
    if 'genero' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'genero is null'}
        return flask.jsonify(response)
    if 'datalancamento' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'datalancamento is null'}
        return flask.jsonify(response)
    if 'duracao' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'duracao is null'}
        return flask.jsonify(response)
    if 'ideditora' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'ideditora is null'}
        return flask.jsonify(response)
    if role != 1:
        response = {'status': StatusCodes["api_error"], 'results': 'Only artists can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO som(titulo, genero, datalancamento, duracao, ideditora) values (%s,%s,%s,%s,%s) RETURNING ismn'
        values = (payload["titulo"], payload["genero"], payload["datalancamento"], payload["duracao"], payload["ideditora"])
        cur.execute(statements, values)
        songID = cur.fetchone()[0]

        statements = 'INSERT INTO artista_som(idartista, som_ismn) values (%s,%s)'
        values = (userID, songID)
        cur.execute(statements, values)
        if 'other_artists' in payload and len(payload['other_artists']) >= 1:
            statements = 'INSERT INTO artista_som(idartista, som_ismn) values' + ' (%s,%s),' * (len(payload['other_artists']) - 1)  + ' (%s,%s)'
            values = []
            for i in payload['other_artists']:
                values += [i, songID]
            cur.execute(statements, values)
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': songID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/album/', methods=['POST'])
@tokenValidation
def addAlbum(userID, role):
    logger.info('POST /album')
    payload = flask.request.get_json()
    if 'titulo' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'titulo is null'}
        return flask.jsonify(response)
    if 'datalancamento' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'datalancamento is null'}
        return flask.jsonify(response)
    if 'nomeeditora' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'nomeeditora is null'}
        return flask.jsonify(response)
    if 'songs' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'songs is null'}
        return flask.jsonify(response)
    if role != 1:
        response = {'status': StatusCodes["api_error"], 'results': 'Only artists can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO album(nome, datalancamento, nomeeditora) values (%s,%s,%s) RETURNING idalbum'
        values = (payload["titulo"], payload["datalancamento"], payload["nomeeditora"])
        cur.execute(statements, values)
        albumID = cur.fetchone()[0]
        if len(payload['songs']) < 1:
            response = {'status': StatusCodes["api_error"], 'results': 'Insufficient songs'}
            return flask.jsonify(response)
        for j in range(len(payload['songs'])):
            songID = 0
            if type(payload['songs'][j]) is not int:
                statements = 'INSERT INTO som(titulo, genero, datalancamento, duracao, ideditora) values (%s,%s,%s,%s,%s) RETURNING ismn'
                values = (payload['songs'][j]["titulo"], payload['songs'][j]["genero"], payload['songs'][j]["datalancamento"], payload['songs'][j]["duracao"],
                          payload['songs'][j]["ideditora"])
                cur.execute(statements, values)
                songID = cur.fetchone()[0]

                statements = 'INSERT INTO artista_som(idartista, som_ismn) values (%s,%s)'
                values = (userID, songID)
                cur.execute(statements, values)
                if 'other_artists' in payload and len(payload['songs'][j]['other_artists']) >= 1:
                    statements = 'INSERT INTO artista_som(idartista, som_ismn) values' + ' (%s,%s),' * (
                                len(payload['songs'][j]['other_artists']) - 1) + ' (%s,%s)'
                    values = []
                    for i in payload['songs'][j]['other_artists']:
                        values += [i, songID]
                    cur.execute(statements, values)
            else:
                songID = payload['songs'][j]
            print(songID)
            statements = 'INSERT INTO ordenarsom(idalbum, som_ismn, ordem) values (%s,%s,%s)'
            values = (albumID, songID, j)
            cur.execute(statements, values)
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': albumID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/song/<keyword>/', methods=['GET'])
@tokenValidation
def searchSong(userID, role, keyword):
    logger.info('GET /song/<keyword>')
    logger.debug(f'keyword: {keyword}')
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f'''SELECT som.titulo, som.genero, som.duracao,som.ideditora, 
                                    array_agg(distinct artista.nomeartista), 
                                    array_agg(distinct ordenarsom.idalbum)
                                FROM som
                                LEFT JOIN ordenarsom ON (som.ismn = ordenarsom.som_ismn)
                                LEFT JOIN artista_som ON (som.ismn = artista_som.som_ismn)
                                LEFT JOIN artista ON (artista.idlogin = artista_som.idartista)
                                WHERE UPPER(som.titulo) LIKE '%{keyword}%'
                                GROUP BY som.ismn''')
        response = []
        rows = cur.fetchall()
        for i in rows:
            response += [{'titulo':i[0], 'genero':i[1], 'duracao':i[2], 'ideditora':i[3], 'albums':i[5], 'artistas':i[4]}]
        response = {'status': StatusCodes['success'], 'results': response}
    except (Exception, psycopg2.DatabaseError) as error:
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/artist_info/<keyword>/', methods=['GET'])
@tokenValidation
def searchArtist(userID, role, keyword):
    logger.info('GET /artistinfo/<keyword>')
    logger.debug(f'keyword: {keyword}')
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f'''SELECT artista.nomeartista, artista.ideditora ,
                            array_agg(distinct artista_som.som_ismn),
                            array_agg(distinct ordenarsom.idalbum),
                            array_agg(distinct som_playlist_publica.idplaylist)
                        FROM artista
                        LEFT JOIN artista_som ON artista_som.idartista = artista.idlogin
                        LEFT JOIN ordenarsom ON ordenarsom.som_ismn = artista_som.som_ismn
                        LEFT JOIN som_playlist_publica ON som_playlist_publica.som_ismn = artista_som.som_ismn
                        GROUP BY artista.idlogin
                        HAVING artista.idlogin = {keyword}
                        ''')
        response = []
        rows = cur.fetchall()
        print(rows)
        for i in rows:
            response += [{'nome':i[0], 'editoraID':i[1], 'songs':i[2], 'albums':i[3], 'playlists':i[4]}]
        response = {'status': StatusCodes['success'], 'results': response}
    except (Exception, psycopg2.DatabaseError) as error:
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/card/', methods=['POST'])
@tokenValidation
def addGiftcard(userID, role):
    logger.info('POST /card')
    payload = flask.request.get_json()
    if 'saldo' not in payload or payload['saldo'] not in ["10","25","50"]:
        response = {'status': StatusCodes["api_error"], 'results': 'saldo is null'}
        return flask.jsonify(response)
    if 'datalimite' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'datalimite is null'}
        return flask.jsonify(response)
    if 'number_cards' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'number_cards is null'}
        return flask.jsonify(response)
    if role != 2:
        response = {'status': StatusCodes["api_error"], 'results': 'Only admins can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO giftcards(idcartao, datalimite, saldo, idadmin) values (%s,%s,%s,%s)'
        values = []
        cards = []
        for i in range(int(payload['number_cards'])):
            cards += [''.join(random.choices(string.digits, k=16))]
            values += [(cards[i], payload['datalimite'], payload['saldo'], userID)]
        cur.executemany(statements, values)

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': cards}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/comments/<song_id>',defaults={'parent_comment_id': None}, methods=['POST'])
@app.route('/comments/<song_id>/<parent_comment_id>', methods=['POST'])
@tokenValidation
def addComments(userID, role, song_id, parent_comment_id):
    logger.info('POST /card')
    payload = flask.request.get_json()
    if 'comment' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'comment is null'}
        return flask.jsonify(response)
    if role == 2:
        response = {'status': StatusCodes["api_error"], 'results': 'Only admins can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO comentarios(comentario,som_ismn,idlogin) values (%s,%s,%s) RETURNING idcomentario'
        values = [payload['comment'],song_id, userID]
        cur.execute(statements, values)
        commentID = cur.fetchone()[0]
        if parent_comment_id is not None:
            statements = 'INSERT INTO respostacomentarios(comentario, resposta) values (%s,%s)'
            values = [parent_comment_id, commentID]
            cur.execute(statements, values)
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': commentID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/<song_id>/', methods=['PUT'])
@tokenValidation
def playSong(userID, role, song_id):
    logger.info('PUT /<song_id>')
    if role != 0:
        response = {'status': StatusCodes["api_error"], 'results': 'Only consumers can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'INSERT INTO atividade(datavisualizacao,idconsumidor, som_ismn) values (NOW(),%s,%s)'
        values = [userID, song_id]
        cur.execute(statements, values)
        conn.commit()
        response = {'status': StatusCodes['success']}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/report/<year_month>', methods=['GET'])
@tokenValidation
def generateReport(userID, role, year_month):
    logger.info('GET /report')
    year_month = year_month
    conn = db_connection()
    cur = conn.cursor()
    try:
        year_month += '01'
        statement = f'''SELECT EXTRACT(MONTH FROM atividade.datavisualizacao) as mes,  som.genero as genero, COUNT(*) as playbacks
                            FROM atividade
                            LEFT JOIN som ON som.ismn = atividade.som_ismn
                            WHERE atividade.datavisualizacao BETWEEN TO_DATE('{year_month}','YYYYMMDD') - (INTERVAL '1 year') AND TO_DATE('{year_month}','YYYYMMDD')
                            GROUP BY mes, genero
                            ORDER BY mes
                            '''
        cur.execute(statement)
        rows = cur.fetchall()
        response = []
        for i in rows:
            response.append({'mes': i[0], 'genero': i[1], 'playbacks': i[2]})
        response = flask.jsonify({'status': 200, 'results': response}), 200
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /user - error: {error}')
        response = flask.jsonify({'status': 500, 'errors': str(error)}), 500
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return response

@app.route('/subcription/', methods=['POST'])
@tokenValidation
def subcribePremium(userID, role):
    logger.info('POST /subcription')
    payload = flask.request.get_json()
    interval = ''
    if role != 0:
        response = {'status': StatusCodes["api_error"], 'results': 'Only costumers can subscribe'}
        return flask.jsonify(response)
    if 'period' not in payload or payload['period'] not in ['MONTH', 'QUARTER', 'SEMESTER']:
        response = {'status': StatusCodes["api_error"], 'results': 'Invalid period'}
        return flask.jsonify(response)
    else:
        if payload['period'].upper() == 'MONTH':
            interval = '1 month'
        elif payload['period'].upper() == 'QUARTER':
            interval = '3 month'
        elif payload['period'].upper() == 'SEMESTER':
            interval = '6 month'
    if 'cards' not in payload or len(payload['cards']) < 1:
        response = {'status': StatusCodes["api_error"], 'results': 'Invalid cards'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statements = 'SELECT idplano, preco FROM plano WHERE duracao = %s'
        values = []
        cur.execute(statements, [payload['period']])
        response = cur.fetchall()
        if len(response) != 1:
            response = {'status': StatusCodes["api_error"], 'results': 'No plan found'}
            return flask.jsonify(response)
        temp = payload['cards']
        cards = str(payload['cards']).replace('[', '(').replace(']', ')')
        print(cards)

        statements = f'UPDATE giftcards SET idconsumidor = %s WHERE idconsumidor is null AND idcartao IN {cards}'

        cur.execute(statements, [userID])

        statements = 'INSERT INTO subcricao(datainicial, idconsumidor, plano_idplano) VALUES (NOW(),%s,%s) RETURNING idsubcricao'
        values = [userID, response[0][0]]
        cur.execute(statements, values)

        subscriptionID = cur.fetchone()[0]

        amount = response[0][1]

        for i in temp:
            cur.execute('SELECT idcartao, saldo FROM giftcards WHERE idcartao = %s AND idconsumidor = %s AND saldo != 0', [i , userID])
            card = cur.fetchall()
            print(i)
            if len(card) < 1:
                response = {'status': StatusCodes["api_error"], 'results': 'Invalid card'}
                return flask.jsonify(response)
            card = card[0]
            if card[1] > amount:
                cur.execute('UPDATE giftcards SET saldo = saldo - %s WHERE idcartao = %s',[amount, card[0]])
                cur.execute('INSERT INTO giftcardutilizado(idcartao, idsubscricao, saldoutilizado) VALUES (%s,%s,%s)', [card[0], subscriptionID, amount])
                break
            else:
                cur.execute('UPDATE giftcards SET saldo = 0 WHERE idcartao = %s', [card[0]])
                cur.execute('INSERT INTO giftcardutilizado(idcartao, idsubscricao, saldoutilizado) VALUES (%s,%s,%s)',[card[0], subscriptionID, card[1]])
                amount = amount - card[1]
        print(interval)
        statements = (f'UPDATE consumidor SET dataPremium = CASE WHEN dataPremium < NOW() THEN NOW()+(INTERVAL \'{interval}\') ELSE dataPremium + INTERVAL \'{interval}\' END WHERE idpessoa = %s')
        cur.execute(statements, [userID])

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': subscriptionID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/playlist/', methods=['POST'])
@tokenValidation
def addPlaylist(userID, role):
    logger.info('POST /playlist')
    payload = flask.request.get_json()
    if 'titulo' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'titulo is null'}
        return flask.jsonify(response)
    if 'songs' not in payload:
        response = {'status': StatusCodes["api_error"], 'results': 'songs is null'}
        return flask.jsonify(response)
    if 'visibilidade' not in payload or payload['visibilidade'].upper() not in ['PUBLIC', 'PRIVATE']:
        response = {'status': StatusCodes["api_error"], 'results': 'Invalid visibility'}
        return flask.jsonify(response)
    if role != 0:
        response = {'status': StatusCodes["api_error"], 'results': 'Only consumers can perform this operation'}
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()
    try:
        statement = "SELECT * FROM consumidor WHERE idpessoa = %s AND dataPremium > NOW()"
        values = [userID]
        cur.execute(statement, values)
        response = cur.fetchall()
        playlistID = 0
        if len(response) != 1:
            response = {'status': StatusCodes["api_error"], 'results': 'Premium not valid'}
            return flask.jsonify(response)
        if payload['visibilidade'] == "PUBLIC":
            statement = "INSERT INTO playlist_publica(playlist_nome, playlist_datacriacao) values (%s,NOW()) RETURNING playlist_idplaylist"
            values = [payload['titulo']]
            cur.execute(statement, values)
            playlistID = cur.fetchone()[0]
            statement = "INSERT INTO som_playlist_publica(idplaylist, som_ismn) VALUES" + " (%s, %s)," * (len(payload['songs']) - 1) + " (%s, %s)"
            values = []
            for song in payload['songs']:
                values += [playlistID, song]
            cur.execute(statement, values)
        if payload['visibilidade'] == "PRIVATE":
            statement = "INSERT INTO playlist_privada(playlist_nome, playlist_datacriacao) values (%s,NOW()) RETURNING playlist_idplaylist"
            values = [payload['titulo']]
            cur.execute(statement, values)
            playlistID = cur.fetchone()[0]
            statement = "INSERT INTO som_playlist_privada(idplaylist, som_ismn) VALUES" + " (%s, %s)," * (len(payload['songs']) - 1) + " (%s, %s)"
            values = []
            for song in payload['songs']:
                values += [playlistID, song]
            cur.execute(statement, values)
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': playlistID}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

if __name__ == '__main__':

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}/dbproj')
