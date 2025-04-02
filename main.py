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
            ).fetchall()  
    except Exception as e:
            print(e)
            boats = []
    if not boats:
        return render_template('search.html', error="No boats found!", boats=None)
    
    return render_template('boats_search.html', error=None, boats=boats)

# boat detail page
@app.route('/boat_info/<int:boat_id>')
def boat_info(boat_id):
    query = text("SELECT * FROM boats WHERE id = :boat_id")
    boat= conn.execute(query, {"boat_id":boat_id}).fetchone()

    if boat:
        return render_template('boat_info.html', boat=boat)
    else:
        return "Boat not found", 404

# delete a boat by ID
@app.route('/delete', methods=['GET'])
def delete_get_request():
    return render_template('boats_delete.html')


@app.route('/delete', methods=['POST'])
def delete_boat():
    try:
        conn.execute(
            text("DELETE FROM boats WHERE id = :id"),
            request.form
        )
        conn.commit()
        return render_template('boats_delete.html', error=None, success="Data deleted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_delete.html', error=error, success=None)

# update
@app.route('/boat/update<int:boat_id>', methods=['GET', 'POST'])
def update_boat(boat_id):
    if request.method == 'GET':
        query = text("SELECT * FROM boats WHERE id = :boat_id")
        boat = conn.execute(query, {"boat_id": boat_id}).fetchone()
        if boat:
            return render_template('boats_update.html', boat=boat)
        else:
            return "Boat not found", 404
    if request.method == 'POST':
        name = request.form['name']
        boat_type = request.form['type']
        owner_id = request.form['owner_id']
        rental_price = request.form['rental_price']

        try:
            conn.execute(
                text("""
                    UPDATE boats 
                    SET name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price
                    WHERE id = :id
                """),
                {"name": name, "type": boat_type, "owner_id": owner_id, "rental_price": rental_price, "id": boat_id}
            )
            conn.commit()
            updated_boat = conn.execute(
                text("SELECT * FROM boats WHERE id = :boat_id"),
                {"boat_id": boat_id}
            ).fetchone()
            return render_template('boat_info.html', boat=updated_boat, success="Boat details updated successfully!")

        except Exception as e:
            error = e.orig.args[1]
            print(error)
            return render_template('boats_update.html', error=error, boat_id=boat_id)


if __name__ == '__main__':
    app.run(debug=True)