from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesViews(Resource):
    def get(self):
        all_movies_ =db.session.query(Movie)
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id:
            all_movies = all_movies_.filter(Movie.director_id == director_id)
            return movies_schema.dump(all_movies), 200
        if genre_id:
            all_movies = all_movies_.filter(Movie.genre_id == genre_id)
            return movies_schema.dump(all_movies), 200


    def post(self):
        try:
            req_json = request.json
            new_movie = Movie(**req_json)
            with db.session.begin():
                db.session.add(new_movie)
            return "", 201
        except Exception as e:
            return str(e)


@movie_ns.route('/<int:mid>')
class MoviesViews(Resource):
    def get(self, mid):

        movie = Movie.query.get(mid)
        return movie_schema.dump(movie)


    def put(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return "", 404
        req_json = request.json
        movie.id = req_json.get("id")
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        try:
            all_directors = db.session.query(Director).all()
            return directors_schema.dump(all_directors), 200
        except Exception as e:
            return str(e)

    def post(self):
        try:
            req_json = request.json
            new_director = Director(**req_json)
            with db.session.begin():
                db.session.add(new_director)
            return "", 201
        except Exception as e:
            return str(e)


@directors_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        if not director:
            return "Not Found", 404
        all_movies = db.session.query(Movie).all()
        movie_in_director = []
        for i in all_movies:
            if i.genre_id == did:
                movie_in_director.append(movie_schema.dump(i))
        return [director_schema.dump(director), movie_in_director], 200

    def put(self, did):
        director = Director.query.get(did)
        if not director:
            return "Not Found", 404
        req_json = request.json
        director.id = req_json.get("id")
        director.name = req_json.get("name")
        db.session.add(Director)
        db.session.commit()

    def delete(self, did):
        director = Director.query.get(did)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        try:
            all_genres = db.session.query(Genre).all()
            return genres_schema.dump(all_genres), 200
        except Exception as e:
            return str(e)

    def post(self):
        try:
            req_json = request.json
            new_genre = Genre(**req_json)
            with db.session.begin():
                db.session.add(new_genre)
            return "", 201
        except Exception as e:
            return str(e)


@genres_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return "Not found", 404
        all_movies = db.session.query(Movie).all()
        movie_in_genre = []
        for i in all_movies:
            if i.genre_id == gid:
                movie_in_genre.append(movie_schema.dump(i))
        return [genre_schema.dump(genre), movie_in_genre], 200

    def put(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return "Not Found", 404
        req_json = request.json
        genre.id = req_json.get("id")
        genre.name = req_json.get("name")
        db.session.add(Director)
        db.session.commit()

    def delete(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=2000)
