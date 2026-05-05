from flask import Flask, render_template, request, redirect
import sqlite3
from deep_translator import GoogleTranslator
from gtts import gTTS

app = Flask(__name__)

# =========================
# 📦 BASE DE DATOS
# =========================
def init_db():
    conn = sqlite3.connect("diccionario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palabras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            espanol TEXT,
            indigena TEXT,
            categoria TEXT,
            ejemplo TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# 🏠 HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    traduccion = ""
    categoria = ""
    ejemplo = ""

    if request.method == "POST":
        palabra = request.form["palabra"].strip().lower()
        direccion = request.form["direccion"]

        conn = sqlite3.connect("diccionario.db")
        cursor = conn.cursor()

        if direccion == "es_ind":
            cursor.execute("SELECT indigena, categoria, ejemplo FROM palabras WHERE espanol=?", (palabra,))
        else:
            cursor.execute("SELECT espanol, categoria, ejemplo FROM palabras WHERE indigena=?", (palabra,))

        resultado = cursor.fetchone()

        if resultado:
            traduccion = resultado[0]
            categoria = resultado[1]
            ejemplo = resultado[2]
        else:
            traduccion = "No encontrada"

        conn.close()

    return render_template("index.html",
        traduccion=traduccion,
        categoria=categoria,
        ejemplo=ejemplo
    )

# =========================
# 🌎 TRADUCCIÓN AJAX
# =========================
@app.route("/traducir_ajax", methods=["POST"])
def traducir_ajax():
    texto = request.form["texto"]
    destino = request.form["destino"]

    if not texto.strip():
        return "Texto vacío"

    try:
        traduccion = GoogleTranslator(source="auto", target=destino).translate(texto)
    except:
        traduccion = "Error al traducir"

    return traduccion

# =========================
# 🔊 AUDIO
# =========================
@app.route("/audio_ajax", methods=["POST"])
def audio_ajax():
    texto = request.form["texto"]
    idioma = request.form["idioma"]

    if not texto.strip():
        return "Texto vacío"

    tts = gTTS(text=texto, lang=idioma)
    tts.save("static/audio.mp3")

    return "ok"

# =========================
# ➕ AGREGAR PALABRA
# =========================
@app.route("/agregar", methods=["POST"])
def agregar():
    espanol = request.form["espanol"].strip().lower()
    indigena = request.form["indigena"].strip().lower()
    categoria = request.form["categoria"]
    ejemplo = request.form["ejemplo"]

    conn = sqlite3.connect("diccionario.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO palabras (espanol, indigena, categoria, ejemplo)
        VALUES (?, ?, ?, ?)
    """, (espanol, indigena, categoria, ejemplo))
    conn.commit()
    conn.close()

    return render_template("guardado.html")

# =========================
# 📚 LISTA
# =========================
@app.route("/lista")
def lista():
    conn = sqlite3.connect("diccionario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, espanol, indigena, categoria, ejemplo FROM palabras")
    datos = cursor.fetchall()
    conn.close()

    return render_template("lista.html", datos=datos)

# =========================
# ❌ ELIMINAR
# =========================
@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = sqlite3.connect("diccionario.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM palabras WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/lista")

# =========================
# ✏️ EDITAR
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = sqlite3.connect("diccionario.db")
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            UPDATE palabras 
            SET espanol=?, indigena=?, categoria=?, ejemplo=? 
            WHERE id=?
        """, (
            request.form["espanol"],
            request.form["indigena"],
            request.form["categoria"],
            request.form["ejemplo"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/lista")

    cursor.execute("SELECT * FROM palabras WHERE id=?", (id,))
    palabra = cursor.fetchone()
    conn.close()

    return render_template("editar.html", palabra=palabra)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
