from flask import Blueprint, request, jsonify
from mysql.connector import Error
from db import get_db_connection

bp = Blueprint("orders", __name__)

# 获取指定 farmer_id 的所有订单（按创建时间降序）
@bp.route("/<int:farmer_id>", methods=["GET"])
def get_orders_by_farmer(farmer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, customer_name, status, total_price, created_at
            FROM orders
            WHERE farmer_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (farmer_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        orders = [
            {
                "id": row[0],
                "customerName": row[1],
                "status": row[2],
                "totalPrice": float(row[3]),
                "createdAt": row[4].isoformat() if row[4] else None
            }
            for row in rows
        ]

        return jsonify(orders)
    except Error as e:
        return jsonify({"error": str(e)}), 500

# 更新指定订单的状态
@bp.route("/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if not new_status:
            return jsonify({"error": "Missing 'status' in request body"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s"
        cursor.execute(query, (new_status, order_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Order status updated successfully."})
    except Error as e:
        return jsonify({"error": str(e)}), 500
