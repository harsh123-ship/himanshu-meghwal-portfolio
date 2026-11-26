from flask import Flask, render_template, jsonify, request
from datetime import datetime
import sqlite3
import os
import threading

app = Flask(__name__)

DATABASE = "portfolio_analytics.db"

LOCK = threading.Lock()


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():

    db = sqlite3.connect(DATABASE)

    db.row_factory = sqlite3.Row

    return db


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():

    with get_db() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS visitors (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                visitor_id TEXT,

                page TEXT,

                event TEXT,

                device TEXT,

                browser TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        db.commit()


init_db()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# ANALYTICS DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


# ==========================================
# VISITOR TRACKING API
# ==========================================

@app.route("/api/track", methods=["POST"])
def track():

    data = request.get_json(silent=True) or {}

    visitor_id = str(
        data.get("visitor_id", "")
    )[:100]

    page = str(
        data.get("page", "/")
    )[:200]

    event = str(
        data.get("event", "page_view")
    )[:100]

    device = str(
        data.get("device", "Unknown")
    )[:50]

    browser = str(
        data.get("browser", "Unknown")
    )[:100]

    if not visitor_id:

        return jsonify({
            "success": False,
            "error": "Visitor ID required"
        }), 400

    with LOCK:

        with get_db() as db:

            db.execute("""

                INSERT INTO visitors

                (
                    visitor_id,
                    page,
                    event,
                    device,
                    browser
                )

                VALUES (?, ?, ?, ?, ?)

            """, (

                visitor_id,
                page,
                event,
                device,
                browser

            ))

            db.commit()

    return jsonify({

        "success": True,

        "message": "Visitor activity recorded",

        "timestamp": datetime.now().isoformat()

    })


# ==========================================
# REAL-TIME ANALYTICS API
# ==========================================

@app.route("/api/analytics")
def analytics():

    with get_db() as db:

        # TOTAL UNIQUE VISITORS

        total = db.execute("""

            SELECT COUNT(DISTINCT visitor_id)

            FROM visitors

        """).fetchone()[0]


        # TODAY VISITORS

        today = db.execute("""

            SELECT COUNT(DISTINCT visitor_id)

            FROM visitors

            WHERE DATE(created_at) = DATE('now')

        """).fetchone()[0]


        # LAST 7 DAYS

        weekly = db.execute("""

            SELECT COUNT(DISTINCT visitor_id)

            FROM visitors

            WHERE created_at >= datetime(
                'now',
                '-7 days'
            )

        """).fetchone()[0]


        # LAST 30 DAYS

        monthly = db.execute("""

            SELECT COUNT(DISTINCT visitor_id)

            FROM visitors

            WHERE created_at >= datetime(
                'now',
                '-30 days'
            )

        """).fetchone()[0]


        # TOTAL PAGE VIEWS

        pageviews = db.execute("""

            SELECT COUNT(*)

            FROM visitors

            WHERE event = 'page_view'

        """).fetchone()[0]


        # ==================================
        # UPDATED DAILY STATISTICS QUERY
        # ==================================

        daily = db.execute("""

            SELECT

                DATE(created_at) AS day,

                COUNT(*) AS visits

            FROM visitors

            WHERE DATE(created_at) >= DATE('now', '-6 days')

            GROUP BY DATE(created_at)

            ORDER BY day ASC

        """).fetchall()


        # ==================================
        # DEVICE STATISTICS
        # ==================================

        devices = db.execute("""

            SELECT

                device,

                COUNT(*) AS total

            FROM visitors

            GROUP BY device

            ORDER BY total DESC

        """).fetchall()


        # ==================================
        # RECENT VISITOR ACTIVITIES
        # ==================================

        activities = db.execute("""

            SELECT

                visitor_id,

                page,

                event,

                device,

                browser,

                created_at

            FROM visitors

            ORDER BY id DESC

            LIMIT 20

        """).fetchall()


    # ==================================
    # JSON RESPONSE
    # ==================================

    return jsonify({

        "success": True,

        "total_visitors": total,

        "today_visitors": today,

        "weekly_visitors": weekly,

        "monthly_visitors": monthly,

        "pageviews": pageviews,

        "daily_statistics": [

            dict(row) for row in daily

        ],

        "devices": [

            dict(row) for row in devices

        ],

        "recent_activities": [

            dict(row) for row in activities

        ],

        "updated_at": datetime.now().isoformat()

    })


# ==========================================
# SERVER HEALTH CHECK
# ==========================================

@app.route("/api/health")
def health():

    return jsonify({

        "status": "online",

        "server": "Flask",

        "database": "SQLite",

        "timestamp": datetime.now().isoformat()

    })


# ==========================================
# CUSTOM 404 ERROR
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "error": "Page not found",

        "available_routes": [

            "/",

            "/dashboard",

            "/api/analytics",

            "/api/track",

            "/api/health"

        ]

    }), 404


# ==========================================
# APPLICATION START
# ==========================================

if __name__ == "__main__":

    print("=" * 55)

    print("HIMANSHU MEGHWAL")

    print("PROFESSIONAL PORTFOLIO BACKEND")

    print("PYTHON ANALYTICS SYSTEM")

    print("=" * 55)

    print("Main Website: http://127.0.0.1:5000")

    print("Dashboard: http://127.0.0.1:5000/dashboard")

    print("Analytics API: http://127.0.0.1:5000/api/analytics")

    print("=" * 55)

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )