from flask import Flask, request, jsonify
import os 
from flask_cors import CORS
import pymysql
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# FIX: Permissive CORS to resolve the 'preflight' error seen in your console
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["UPLOAD_FOLDER"] = "static/images"

def get_db_connection():
    return pymysql.connect(
        host="mysql-keyafidel.alwaysdata.net", 
        user="keyafidel", 
        password="modcom1234", 
        database="keyafidel_sokogarden"
    )

@app.route("/api/signup" , methods = ["POST"])
def signup():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    phone = request.form["phone"]
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO users(username,email,phone,password) VALUES(%s,%s,%s,%s)"
    cursor.execute(sql, (username, email, phone, password))
    connection.commit()
    connection.close()
    return jsonify({"message" : "User registered successfully"})  

@app.route("/api/signin" , methods=["POST"])
def signin():
    email = request.form["email"]
    password = request.form["password"]
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()
    connection.close()
    if user:
        return jsonify({"message" : "user logged in successfully" , "user":user})
    return jsonify({"message" : "login failed"}), 401

@app.route("/api/add_product" , methods = ["POST"])
def Addproducts():
    product_name = request.form["product_name"]
    product_description = request.form["product_description"]
    product_cost = request.form["product_cost"]
    product_photo = request.files["product_photo"]
    filename = product_photo.filename 
    photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    product_photo.save(photo_path)
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO product_details(product_name, product_description, product_cost, product_photo) VALUES(%s,%s,%s,%s)"
    cursor.execute(sql, (product_name, product_description, product_cost, filename))
    connection.commit() 
    connection.close()
    return jsonify({"message" : "Product added successfully"}) 

@app.route("/api/get_products")
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM product_details")
    products = cursor.fetchall()
    connection.close()
    return jsonify(products)

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"message": "Email is required"}), 400
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # Ensure the 'subscribers' table exists in your AlwaysData DB
        cursor.execute("INSERT INTO subscribers (email) VALUES (%s)", (email,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Welcome to the Lumine Insider circle!"}), 200
    except pymysql.err.IntegrityError:
        return jsonify({"message": "This email is already part of the circle."}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    amount = request.form['amount']
    phone = request.form['phone']
    # Keep your existing Safaricom API credentials here
    return jsonify({"message": "Please Complete Payment in Your Phone"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)