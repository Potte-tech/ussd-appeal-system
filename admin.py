from flask import Flask, request, redirect, render_template, session, url_for
from utils.db import get_connection
from werkzeug.security import check_password_hash

app.secret_key = 'your_secret_key_here'  # Use a secure, random key

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM admins WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Login failed"

    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, module_name, reason, status FROM appeals")
    appeals = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', appeals=appeals)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))
