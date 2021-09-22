from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired
import requests
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_list.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api_key = "7ebfeb66469554dce1dac6d405fcf7c3"


# Model the movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# Create the DB
# db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()

class MovieForm(FlaskForm):
    rating = FloatField('Edit rating')
    review = StringField('Edit review')
    submit = SubmitField('Submit')


class NewMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit-rating", methods=["GET", "POST"])
def edit_rating():
    form = MovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route('/delete-book')
def delete_movie():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = NewMovieForm()
    if form.validate_on_submit():
        search_query = request.form["title"]
        search_page = "1"
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={urllib.parse.quote(search_query)}&page={search_page}&language=en&include_adult=false"
        response = requests.get(search_url)
        movies = []
        for result in response.json()["results"]:
            movies.append({'title': result["title"], 'release_date': result["release_date"], 'id': result["id"]})
        return render_template("select.html", movies=movies)
    return render_template("add.html", form=form)


@app.route("/select", methods=["GET"])
def select():
    movie_id = request.args.get('movie_id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)

    print(response.json()["title"], response.json()["poster_path"], response.json()["release_date"][0:4], response.json()["overview"])
    movie = Movie (
        title=response.json()["title"],
        img_url=response.json()["poster_path"],
        year=int(response.json()["release_date"][0:4]),
        description=response.json()["overview"],
        rating=0.0,
        ranking=0,
        review=""
    )
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for("edit_rating", id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)

