# routes/products.py

from flask import Blueprint, request, jsonify
from db import get_db_connection
from mysql.connector import Error

products_bp = Blueprint('products', __name__)

@products_bp.route("", methods=["GET"])
@products_bp.route("/", methods=["GET"])
def list_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
          id, farmer_id, name, description, price, quantity,
          image_url, category, updated_at
        FROM products
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    products = [{
        "id":          r[0],
        "farmerId":    r[1],
        "name":        r[2],
        "description": r[3],
        "price":       float(r[4]),
        "quantity":    r[5],
        "imageUrl":    r[6],
        "category":    r[7],
        "updatedAt":   r[8].isoformat() + "Z"
    } for r in rows]

    return jsonify(products), 200

@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
              id, farmer_id, name, description, price, quantity,
              image_url, category, updated_at
            FROM products
            WHERE id = %s
        """, (product_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row is None:
            return jsonify({"error": "Product not found"}), 404

        product = {
            "id":          row[0],
            "farmerId":    row[1],
            "name":        row[2],
            "description": row[3],
            "price":       float(row[4]),
            "quantity":    row[5],
            "imageUrl":    row[6],
            "category":    row[7],
            "updatedAt":   row[8].isoformat() + "Z"
        }
        return jsonify(product), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500



@products_bp.route("/", methods=["POST"])
def create_product():
    data        = request.get_json()
    farmer_id   = data.get("farmer_id")
    name        = data.get("name")
    description = data.get("description", "")
    price       = data.get("price", 0.0)
    quantity    = data.get("quantity", 0)
    image_url   = data.get("image_url", "")
    category    = data.get("category", "uncategorized")

    if not farmer_id or not name:
        return jsonify({"error": "farmer_id and name are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO products
              (farmer_id, name, description, price, quantity, image_url, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            farmer_id, name, description, price, quantity, image_url, category
        ))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            "id":          new_id,
            "farmerId":    farmer_id,
            "name":        name,
            "description": description,
            "price":       price,
            "quantity":    quantity,
            "imageUrl":    image_url,
            "category":    category,
            # updatedAt 由数据库自动生成
        }), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data   = request.get_json()
    fields = []
    values = []

    # 允许更新 category
    for key in ("name", "description", "price", "quantity", "image_url", "category"):
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(product_id)
    sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Product updated"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Product deleted"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
