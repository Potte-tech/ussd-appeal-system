from flask import Flask, request, make_response
from utils.db import get_connection
import datetime

app = Flask(__name__)

# Sessions: track temporary interactions for 5 minutes
sessions = {}

@app.route("/ussd", methods=["POST"])  # ✅ CHANGED from "/" to "/ussd"
def ussd_callback():
    session_id = request.form.get("sessionId")
    service_code = request.form.get("serviceCode")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text")

    # Reset session if more than 5 minutes
    now = datetime.datetime.now()
    if session_id in sessions:
        if (now - sessions[session_id]['timestamp']).seconds > 300:
            del sessions[session_id]

    if session_id not in sessions:
        sessions[session_id] = {
            'level': 0,
            'student_id': '',
            'module': '',
            'reason': '',
            'timestamp': now
        }

    parts = text.split("*")
    response = ""

    if text == "":
        response = "CON Welcome to the Marks Appeal System\n"
        response += "1. Check my marks\n"
        response += "2. Appeal my marks\n"
        response += "3. Check appeal status\n"

    elif parts[0] == "1":  # ✅ Option 1: Check marks
        if len(parts) == 1:
            response = "CON Enter your Student ID:"
        elif len(parts) == 2:
            student_id = parts[1]
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT module_name, mark FROM marks WHERE student_id = %s", (student_id,))
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    marks = "\n".join([f"{row[0]}: {row[1]}" for row in rows])
                    response = f"END Your marks:\n{marks}"
                else:
                    response = "END Error: Student ID not found."
            except Exception as e:
                response = f"END Database error: {str(e)}"

    elif parts[0] == "2":  # ✅ Option 2: Appeal
        if len(parts) == 1:
            response = "CON Enter your Student ID:"
        elif len(parts) == 2:
            response = "CON Enter module name to appeal:"
        elif len(parts) == 3:
            response = "CON Enter reason for appeal:"
        elif len(parts) == 4:
            student_id = parts[1]
            module = parts[2]
            reason = parts[3]
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO appeals (student_id, module_name, reason, status) VALUES (%s, %s, %s, 'Pending')",
                    (student_id, module, reason))
                conn.commit()
                conn.close()
                response = "END Appeal submitted successfully."
            except Exception as e:
                response = f"END Database error: {str(e)}"

    elif parts[0] == "3":  # ✅ Option 3: Check appeal status
        if len(parts) == 1:
            response = "CON Enter your Student ID:"
        elif len(parts) == 2:
            student_id = parts[1]
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT module_name, status FROM appeals WHERE student_id = %s", (student_id,))
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    status = "\n".join([f"{row[0]}: {row[1]}" for row in rows])
                    response = f"END Appeal Status:\n{status}"
                else:
                    response = "END No appeals found for that ID."
            except Exception as e:
                response = f"END Database error: {str(e)}"

    else:
        response = "END Invalid option. Please try again."

    return make_response(response, 200, {'Content-Type': 'text/plain'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

