from flask import Blueprint, request, jsonify
from mysql.connector import Error
from db import get_db_connection

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/<int:farmer_id>", methods=["GET"])
def get_sales_by_farmer(farmer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                DATE(created_at) AS date,
                COUNT(*) AS orders,
                SUM(total_price) AS revenue,
                SUM(total_quantity) AS products
            FROM orders
            WHERE farmer_id = %s
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """
        cursor.execute(query, (farmer_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        result = [
            {
                "date": row[0].isoformat(),
                "orders": row[1],
                "revenue": float(row[2]) if row[2] is not None else 0.0,
                "products": row[3] if row[3] is not None else 0
            }
            for row in rows
        ]

        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
