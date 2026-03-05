from flask import Flask, request, jsonify
import psycopg2
import requests

app = Flask(__name__)

# NeonDB
conn = psycopg2.connect("postgresql://neondb_owner:npg_m8LEJPzVH7jw@ep-sweet-mode-ai35kmho-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
API_KEY="EBQAD_SECURE_2026"
FREEMIG_UPLOAD_URL="https://freemig.example.com/api/upload"  # ضع رابط Freemig الصحيح هنا

@app.route("/api/upload", methods=["POST"])
def upload():
    if request.headers.get("X-API-KEY") != API_KEY: return jsonify({"error":"Unauthorized"}),401
    file = request.files.get("file")
    if not file: return jsonify({"error":"No file"}),400
    files = {'file': (file.filename, file.stream, file.mimetype)}
    r = requests.post(FREEMIG_UPLOAD_URL, files=files)
    if r.status_code==200: return jsonify({"url": r.json().get("url")})
    return jsonify({"error":"Upload failed"}),500

@app.route("/api/projects", methods=["GET","POST"])
def projects():
    cur = conn.cursor()
    if request.method=="POST":
        data=request.get_json()
        cur.execute("INSERT INTO projects(title,description,tech_stack,image_url) VALUES(%s,%s,%s,%s) RETURNING id",
                    (data['title'],data.get('description'),data.get('tech_stack'),data.get('image_url')))
        conn.commit(); pid=cur.fetchone()[0]
        return jsonify({"id":pid})
    cur.execute("SELECT id,title,description,tech_stack,image_url FROM projects ORDER BY id DESC")
    return jsonify([{"id":r[0],"title":r[1],"description":r[2],"tech_stack":r[3],"image_url":r[4]} for r in cur.fetchall()])

@app.route("/api/projects/<int:pid>", methods=["PUT","DELETE"])
def modify_project(pid):
    cur = conn.cursor()
    if request.method=="PUT":
        data=request.get_json()
        cur.execute("UPDATE projects SET title=%s,description=%s,tech_stack=%s,image_url=%s WHERE id=%s",
                    (data['title'],data.get('description'),data.get('tech_stack'),data.get('image_url'),pid))
        conn.commit(); return jsonify({"status":"ok"})
    elif request.method=="DELETE":
        cur.execute("DELETE FROM projects WHERE id=%s",(pid,))
        conn.commit(); return jsonify({"status":"deleted"})

@app.route("/api/messages", methods=["GET","POST","DELETE"])
def messages():
    cur = conn.cursor()
    if request.method=="GET":
        cur.execute("SELECT id,name,email,message FROM messages ORDER BY id DESC")
        return jsonify([{"id":m[0],"name":m[1],"email":m[2],"message":m[3]} for m in cur.fetchall()])
    elif request.method=="POST":
        data=request.get_json()
        cur.execute("INSERT INTO messages(name,email,message) VALUES(%s,%s,%s)",(data['name'],data['email'],data['message']))
        conn.commit(); return jsonify({"status":"ok"})
    elif request.method=="DELETE":
        pid=request.args.get("id")
        cur.execute("DELETE FROM messages WHERE id=%s",(pid,))
        conn.commit(); return jsonify({"status":"deleted"})

@app.route("/api/about", methods=["GET","POST"])
def about():
    cur=conn.cursor()
    if request.method=="GET":
        cur.execute("SELECT content FROM about ORDER BY id DESC LIMIT 1")
        r=cur.fetchone()
        return jsonify({"content":r[0] if r else ""})
    elif request.method=="POST":
        data=request.get_json()
        cur.execute("INSERT INTO about(content) VALUES(%s)",(data['content'],))
        conn.commit(); return jsonify({"status":"ok"})

if __name__=="__main__":
    app.run(debug=True)
