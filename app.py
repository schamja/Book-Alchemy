import os
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from dotenv import load_dotenv
from data_models import db, Author, Book

# 1. Umgebungsvariablen laden
load_dotenv()

app = Flask(__name__)

# 2. Konfiguration
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'standard-geheimnis')
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, 'data')

if not os.path.exists(data_path):
    os.makedirs(data_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(data_path, 'library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Datenbank initialisieren
db.init_app(app)


# --- ROUTEN (Müssen vor app.run stehen) ---

@app.route('/')
def home():
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'title')

    query = Book.query.join(Author)

    # Implementierung der Suche nach Titel ODER Autor
    if search_query:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{search_query}%'),
                Author.name.ilike(f'%{search_query}%')
            )
        )

    # Sortierung
    if sort_by == 'author':
        query = query.order_by(Author.name)
    elif sort_by == 'year':
        query = query.order_by(Book.publication_year.desc())
    else:
        query = query.order_by(Book.title)

    books = query.all()
    return render_template('home.html', books=books, search_query=search_query)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        pub_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')
        rating = request.form.get('rating')

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=pub_year,
            author_id=author_id,
            rating=int(rating) if rating else 5
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f"Buch '{title}' hinzugefügt!", "success")
        return redirect(url_for('home'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        date_of_death = request.form.get('date_of_death')

        if name:
            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            flash(f"Autor '{name}' hinzugefügt!", "success")
            return redirect(url_for('home'))
    return render_template('add_author.html')


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()

    flash("Gelöscht.", "success")
    return redirect(url_for('home'))


# 4. App starten
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)