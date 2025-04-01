from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:CSET155@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


# render a file
@app.route('/')
def index():
    return render_template('index.html')


# remember how to take user inputs?
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# get all boats
# this is done to handle requests for two routes -
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    page = int(page)  # request params always come as strings. So type conversion is necessary.
    per_page = 10  # records to show per page
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    print(boats)
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)


@app.route('/create', methods=['GET'])
def create_get_request():
    return render_template('boats_create.html')


@app.route('/create', methods=['POST'])
def create_boat():
    # you can access the values with request.from.name
    # this name is the value of the name attribute in HTML form's input element
    # ex: print(request.form['id'])
    try:
        conn.execute(
            text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
            request.form
        )
        conn.commit()
        return render_template('boats_create.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_create.html', error=error, success=None)


@app.route('/search', methods=['GET'])

def search_boat():
    search_query = request.args.get('query')
    boats=[]
    try:
            boats = conn.execute(
                text("SELECT * FROM boats WHERE id = :search_query OR name LIKE :search_query OR type LIKE :search_query"),
                {"search_query": search_query}
            ).fetchall()  # Fetch all results
    except Exception as e:
            print(e)
            boats = []
    if not boats:
        return render_template('search.html', error="No boats found!", boats=None)
    
    return render_template('boats_search.html', error=None, boats=boats)
 

if __name__ == '__main__':
    app.run(debug=True)








# from flask import Flask, render_template, request, redirect, url_for
# from sqlalchemy import create_engine, text

# app = Flask(__name__)
# conn_str = "mysql://root:CSET155@localhost/boatdb"
# engine = create_engine(conn_str, echo=True)


# # render a file
# @app.route('/')
# def index():
#     return render_template('index.html')


# # get all boats
# @app.route('/boats/')
# @app.route('/boats/<page>')
# def get_boats(page=1):
#     page = int(page)
#     per_page = 10  # records to show per page
#     boats = engine.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).fetchall()
#     return render_template('boats.html', boats=boats, page=page, per_page=per_page)


# @app.route('/create', methods=['GET'])
# def create_get_request():
#     return render_template('boats_create.html')


# @app.route('/create', methods=['POST'])
# def create_boat():
#     try:
#         engine.execute(
#             text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
#             request.form
#         )
#         engine.commit()
#         return render_template('boats_create.html', error=None, success="Data inserted successfully!")
#     except Exception as e:
#         error = "An error occurred while inserting data. Please try again."
#         return render_template('boats_create.html', error=error)


# @app.route('/search', methods=['GET'])
# def search_boat():
#     search_query = request.args.get('query')
#     boats = []
#     try:
#         boats = engine.execute(
#             text("SELECT * FROM boats WHERE id = :search_query OR name LIKE :search_query OR type LIKE :search_query"),
#             {"search_query": search_query}
#         ).fetchall()
#     except Exception as e:
#         boats = []
#     if not boats:
#         return render_template('search.html', error="No boats found!", boats=None)
    
#     return render_template('boats_search.html', error=None, boats=boats)


# @app.route('/boat/<int:boat_id>')
# def boat_detail(boat_id):
#     boat = engine.execute(
#         text("SELECT * FROM boats WHERE id = :boat_id"),
#         {"boat_id": boat_id}
#     ).fetchone()
#     if not boat:
#         return "Boat not found!", 404
#     return render_template('boat_detail.html', boat=boat)


# @app.route('/delete_boat/<int:boat_id>', methods=['POST'])
# def delete_boat(boat_id):
#     try:
#         result = engine.execute(
#             text("DELETE FROM boats WHERE id = :boat_id"),
#             {"boat_id": boat_id}
#         )
#         engine.commit()
#         if result.rowcount == 0:
#             return "Boat not found!", 404
#         return redirect(url_for('get_boats'))
#     except Exception as e:
#         return f"An error occurred: {e}", 500


# @app.route('/edit_boat/<int:boat_id>', methods=['GET', 'POST'])
# def edit_boat(boat_id):
#     if request.method == 'GET':
#         boat = engine.execute(
#             text("SELECT * FROM boats WHERE id = :boat_id"),
#             {"boat_id": boat_id}
#         ).fetchone()
#         if not boat:
#             return "Boat not found!", 404
#         return render_template('edit_boat.html', boat=boat)
    
#     if request.method == 'POST':
#         updated_data = {
#             'name': request.form['name'],
#             'type': request.form['type'],
#             'owner_id': request.form['owner_id'],
#             'rental_price': request.form['rental_price'],
#             'boat_id': boat_id
#         }
#         try:
#             engine.execute(
#                 text("""
#                     UPDATE boats
#                     SET name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price
#                     WHERE id = :boat_id
#                 """),
#                 updated_data
#             )
#             engine.commit()
#             return redirect(url_for('boat_detail', boat_id=boat_id))
#         except Exception as e:
#             return f"An error occurred: {e}", 500


# if __name__ == '__main__':
#     app.run(debug=True)


