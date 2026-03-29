from flask import Flask, request, redirect, send_from_directory, jsonify, session, url_for
from functools import wraps
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Credenciales simples y seguras (ajustar en entorno real)
ADMIN_USER = 'admin'
ADMIN_PASSWORD = 'password123'

# Configuración para carga de archivos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
POSTS_METADATA_FILE = 'posts_metadata.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crear carpetas si no existen
if not os.path.exists('assets'):
    os.makedirs('assets')
if not os.path.exists('posts'):
    os.makedirs('posts')

def load_posts_metadata():
    if os.path.exists(POSTS_METADATA_FILE):
        with open(POSTS_METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_posts_metadata(metadata):
    with open(POSTS_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return wrapped

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            next_page = request.args.get('next') or url_for('admin')
            return redirect(next_page)
        return "Usuario o contraseña incorrectos", 401
    return send_from_directory('.', 'login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/crear-blog')
def crear_blog():
    return redirect(url_for('login', next=url_for('admin')))

@app.route('/admin')
@login_required
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/posts')
def api_posts():
    posts = [f.replace('.html', '') for f in os.listdir('posts') if f.endswith('.html')]
    metadata = load_posts_metadata()
    
    posts_data = []
    for post in posts:
        post_info = {
            'title': post.replace('-', ' ').title(),
            'slug': post
        }
        if post in metadata:
            post_info['cover'] = metadata[post].get('cover')
        posts_data.append(post_info)
    
    return jsonify({'posts': posts_data})

@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    post_slug = title.lower().replace(' ', '-')
    filename = post_slug + '.html'
    
    # Manejo de imagen de portada (requerida)
    cover_path = None
    if 'cover' in request.files:
        file = request.files['cover']
        if file and file.filename and allowed_file(file.filename):
            original_ext = file.filename.rsplit('.', 1)[1].lower()
            cover_filename = post_slug + '-cover.' + original_ext
            cover_path = os.path.join('assets', cover_filename)
            file.save(cover_path)
    
    # Manejo de imagen del cuerpo (opcional)
    image_html = ""
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            original_ext = file.filename.rsplit('.', 1)[1].lower()
            image_filename = post_slug + '-body.' + original_ext
            image_path = os.path.join('assets', image_filename)
            file.save(image_path)
            image_html = f'<img src="../assets/{image_filename}" alt="{title}" style="max-width: 100%; height: auto;"><br><br>'
    
    # Guardar metadatos del post
    metadata = load_posts_metadata()
    metadata[post_slug] = {
        'title': title,
        'cover': 'assets/' + os.path.basename(cover_path) if cover_path else None,
        'summary': summary
    }
    save_posts_metadata(metadata)
    
    with open(f'posts/{filename}', 'w') as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header>
        <h1>My Blog</h1>
        <nav>
            <a href="../index.html">Home</a>
            <a href="../publicaciones.html">PUBLICACIONES</a>
            <a href="../redes.html">REDES</a>
            <a href="../conocenos.html">CONOCENOS</a>
        </nav>
    </header>
    <main>
        <article>
            <h2>{title}</h2>
            <p><em>{summary}</em></p>
            {image_html}
            <p>{content}</p>
        </article>
    </main>
    <footer>
        <p>&copy; 2026 My Blog</p>
    </footer>
    <script src="../js/script.js"></script>
</body>
</html>''')
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)