# app.py
from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
from routes.products import products_bp
from routes.orders import bp as orders_bp
from routes.sales import sales_bp
from db import get_db_connection

load_dotenv()  # 加载 .env

app = Flask(__name__)
app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(orders_bp, url_prefix="/api/orders")
app.register_blueprint(sales_bp, url_prefix="/api/sales")
# app.py（在文件最上面）  
import os  
print("Loading env vars:")  
print("  DB_HOST    =", os.getenv("DB_HOST"))  
print("  DB_USER    =", os.getenv("DB_USER"))  
print("  DB_PASSWORD=", os.getenv("DB_PASSWORD"))  
print("  DB_NAME    =", os.getenv("DB_NAME"))  
# 其余代码不变...

@app.route("/")
def index():
    return "🚜 Farmers Marketplace API is running!"

@app.route("/products")
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, quantity FROM products")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        products = [
            {"id": row[0], "name": row[1], "price": float(row[2]), "quantity": row[3]}
            for row in rows
        ]
        return jsonify(products)
    except Error as e:
        # 如果出错，返回 500 和错误信息
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # debug 模式下自动重载，并显示详细错误
    app.run(debug=True, host="0.0.0.0", port=5000)
