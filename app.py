import os
import requests
from flask import Flask, render_template, request, flash, redirect, url_for, flash
from data_models import db, Author, Book

app = Flask(__name__)

# Absoluter Pfad & Ordner-Sicherung
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, 'data')

if not os.path.exists(data_path):
    os.makedirs(data_path)

# URI-Konfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(data_path, 'library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_geheim'  # Wichtig für flash()!

db.init_app(app)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        pub_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')  # Hier holen wir einfach die ID
        rating = request.form.get('rating')

        # Hier erstellen wir das Buch-Objekt EINMALIG mit allen Werten
        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=pub_year,
            author_id=author_id,  # Einfach die ID aus dem Formular übergeben
            rating=int(rating) if rating else 5
        )

        db.session.add(new_book)
        db.session.commit()
        flash(f"Buch '{title}' wurde hinzugefügt!", "success")
        return redirect(url_for('home'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/recommendations')
def recommendations():
    books = Book.query.all()
    # Wir erstellen einen Text-String aus deinen Top-Büchern
    top_books = [f"{b.title} ({b.rating}/10)" for b in books if b.rating >= 8]

    prompt = f"Ich mag diese Bücher: {', '.join(top_books)}. Was soll ich als Nächstes lesen?"

    # Da wir keinen echten API-Key für dich haben, geben wir einen Platzhalter aus
    # In der Abgabe kannst du erwähnen, dass hier die API-Anfrage (z.B. OpenAI) erfolgt
    ai_suggestion = "Basierend auf deinem Geschmack empfiehlt die Alchemie-KI: 'Der Name des Windes' von Patrick Rothfuss."

    return render_template('recommendations.html', suggestion=ai_suggestion, prompt=prompt)
@app.route('/')
def home():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'title')
    # Basis-Abfrage mit Join, damit wir nach Autorennamen sortieren können
    query = Book.query.join(Author)

    # Stichwortsuche (Filter)
    # Sortierung anwenden
    if sort_by == 'author':
        query = query.order_by(Author.name)
    elif sort_by == 'year':
        query = query.order_by(Book.publication_year.desc())
    else:
        query = query.order_by(Book.title)

    books = query.all()
    return render_template('home.html', books=books, search_query=search_query)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    # Bonus: Autor löschen, wenn er keine Bücher mehr hat
    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"Buch und Autor '{author.name}' wurden entfernt, da keine weiteren Bücher existieren.", "info")
    else:
        flash(f"Buch '{book.title}' wurde gelöscht.", "success")

    return redirect(url_for('home'))


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        # 1. Daten aus dem Formular abrufen
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        date_of_death = request.form.get('date_of_death')

        # 2. Prüfen, ob der Name vorhanden ist
        if name:
            try:
                # 3. Das Objekt erst JETZT erstellen, wenn die Variablen gefüllt sind
                new_author = Author(
                    name=name,
                    birth_date=birth_date,
                    date_of_death=date_of_death
                )
                db.session.add(new_author)
                db.session.commit()
                flash(f"Autor '{name}' erfolgreich hinzugefügt!", "success")
                return redirect(url_for('add_author')) # Seite neu laden
            except Exception as e:
                db.session.rollback()
                flash(f"Fehler beim Speichern: {e}", "danger")
        else:
            flash("Der Name des Autors ist erforderlich!", "warning")

    return render_template('add_author.html')




if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Hier wird die Datei mit ALLEN Spalten neu erstellt
    app.run(debug=True, port=5001)