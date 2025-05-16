from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = '123456789'  # Needed for flash messages

# Function to establish a database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",  # Default user for XAMPP
        password="",  # Default password is empty for root
        database="stock"  # Replace with your database name
    )
    return connection

# Route to display the home page with current products
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")  # Adjust based on your table structure
    products = cursor.fetchall()  # Fetch all rows from the products table
    cursor.close()
    connection.close()
    return render_template('index.html', products=products)

# Route to display current inventory
@app.route('/inventory', methods=['GET'])
def current_inventory():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to fetch row data as dictionaries

    # Fetch all records from 'products' table
    cursor.execute("SELECT HSN, name, quantity FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    # Render the inventory template with fetched data
    return render_template('current_inventory.html', products=products)

# Route to add a new product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        hsn = request.form['hsn']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (HSN, name, quantity) VALUES (%s, %s, %s)", (hsn, name, quantity))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('index'))

    return render_template('add_products.html')

# Route to update a product using the HSN value
@app.route('/update/<HSN>', methods=['GET', 'POST'])
def update_product(HSN):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        new_quantity = request.form['quantity']
        cursor.execute("UPDATE products SET quantity = %s WHERE HSN = %s", (new_quantity, HSN))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('view_inventory'))

    cursor.execute("SELECT * FROM products WHERE HSN = %s", (HSN,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()

    if product:
        return render_template('update_product.html', product=product)
    else:
        return "Product not found", 404

@app.route('/view', methods=['GET'])
def view_inventory():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get search query from request
    search_query = request.args.get('search')

    # SQL query with search functionality
    if search_query:
        query = "SELECT * FROM products WHERE HSN LIKE %s OR name LIKE %s"
        cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('view_inventory.html', products=products)

if __name__ == "__main__":
    app.run(debug=True)
