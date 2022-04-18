#################################################
## {                                           ##
##      name: REST_FLASK 0.1 (micro-rest),     ##
##      description: Generic REST for          ##
##                   prototyping and rapid     ##
##                   development.              ##
##      author: Artur Juvé Vidal,              ##
##      date: june 2020,                       ##
##      requires:[                             ##
##           pip install flask,                ##
##           pip install passlib,              ##
##           pip install mysql-client,         ##
##           pip install mysql.connector,      ##
##        ]                                    ##
## }                                           ##
#################################################

from flask import Flask, request, jsonify, abort, session
from flask.json import JSONEncoder
from datetime import date
from passlib.hash import sha256_crypt as pwd_context
from functools import wraps
import mysql.connector
import json

#configuration
###############################################
app = Flask(__name__)
app.secret_key = 'secret-key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="empresa"
)
app.host = '0.0.0.0'
app.port = 3000
app.tables = ['departament','empleat','foo']

app.guest_enable = False
app.guest_writable = False
app.username = 'admin'
app.password = '12345'

app.debug = True

#authentificate
###############################################
def require_authentication_guest_enable(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            username = request.authorization.username
            password = request.authorization.password
        except Exception as ex:
            username = None
            password = None        

        if not app.guest_enable:
            if username!=app.username or password!=app.password:
                print(f"Unauthorized access")
                return jsonify(False)

        return func(*args, **kwargs)
    return decorator

def require_authentication_guest_writable(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            username = request.authorization.username
            password = request.authorization.password
        except Exception as ex:
            username = None
            password = None        

        if not app.guest_enable and not app.guest_writable:
            if username!=app.username or password!=app.password:
                print(f"Unauthorized access")
                return jsonify(False)

        return func(*args, **kwargs)
    return decorator

#json encoder
###############################################
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
                #return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

#generic rest (made it for every entity)
###############################################
def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator

def rest(tablename):
    
    @app.route(f"/{tablename}/", methods=['GET'])
    @require_authentication_guest_enable
    @rename(f"get_items_{tablename}")
    def get_items():
        return all(tablename)
    
    @app.route(f"/{tablename}/count", methods=['GET'])
    @require_authentication_guest_enable
    @rename(f"count_items_{tablename}")
    def count_items():
        return count(tablename)    
    
    @app.route(f"/{tablename}/<id>", methods=['GET'])
    @require_authentication_guest_enable
    @rename(f"get_item_{tablename}")
    def get_item(id):
        return index(tablename,id)

    @app.route(f"/{tablename}/<id>", methods=['DELETE'])
    @require_authentication_guest_writable
    @rename(f"delete_item_{tablename}")
    def delete_item(id):
        return delete(tablename,id)
        
    @app.route(f"/{tablename}/", methods=['POST'])
    @require_authentication_guest_writable
    @rename(f"insert_item_{tablename}")
    def insert_item():
        return insert(tablename)        
        
    @app.route(f"/{tablename}/<id>", methods=['PUT'])
    @require_authentication_guest_writable
    @rename(f"update_item_{tablename}")
    def update_item(id):
        return update(tablename,id)          

#call rest tables
###############################################
for tablename in app.tables:
    rest(tablename)

#route not found
###############################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify("Error")

#database crud (not touch)
###############################################

def all(tablename,orderby=None,limit1=None,limit2=None):
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(f" SELECT * FROM {tablename} ")
        objs = cur.fetchall()

        return jsonify(objs)        
    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify(False)
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass

def count(tablename):
    try:
        cur = db.cursor()
        cur.execute(f"SELECT count(*) FROM {tablename}")
        res = cur.fetchall()[0][0]

        return jsonify(res)        
    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify(False)
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass

def index(tablename,id):
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {tablename} WHERE id={id}")
        obj = cur.fetchall()[0]

        return jsonify(obj)        
    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify(False)
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass
    
def delete(tablename, id):
    try:
        cur = db.cursor()
        cur.execute(f"DELETE FROM {tablename} WHERE id = {id}")
        db.commit()
        return jsonify(True)
    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify(Error)
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass
            
def insert(tablename):
    try:
        dict_data = json.loads(request.data)
        placeholders = ', '.join(['%s'] * len(dict_data))
        columns = ', '.join(dict_data.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tablename, columns, placeholders)  

        values = dict_data.values()
        cur = db.cursor()
        cur.execute(sql, list(dict_data.values()))
        db.commit()

        if cur.rowcount>0:
            return jsonify(True)
        else:
            return jsonify(False)

    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify("Error")
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass    

def update(tablename,id):
    try:
        dict_data = json.loads(request.data)
        sets = ', '.join(map(lambda x: str(x) + '= %s ',dict_data.keys()))
        where = "id=%s"
        
        sql = "UPDATE %s SET %s WHERE %s" % (tablename, sets, where)
        
        cur = db.cursor()
        cur.execute(sql, list(dict_data.values()) + [id])    
        db.commit()
        
        if cur.rowcount>0:
            return jsonify(True)
        else:
            return jsonify(False)

    except Exception as ex:
        if app.debug:
            print(ex)
        return jsonify("Error")
    finally:
        try:
            cur.close()
        except Exception as ex:
            pass


if __name__ == '__main__':
    app.run(host=app.host, port=app.port, debug=True)
