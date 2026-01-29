from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Stelle sicher, dass diese Namen exakt so geschrieben sind:
    birth_date = db.Column(db.String(50))
    date_of_death = db.Column(db.String(50))

    books = db.relationship('Book', backref='author', lazy=True)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    publication_year = db.Column(db.Integer)

    rating = db.Column(db.Integer, default=5)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)