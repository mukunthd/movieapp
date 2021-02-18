import os 
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

import tmdbsimple as tmdb
tmdb.API_KEY = os.getenv('API_KEY')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Test123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB_HOST = os.getenv('DB_HOST1')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@' + DB_HOST
db = SQLAlchemy(app)

class MyForm(FlaskForm):
    Language = SelectField(u'Select the Language', choices=['English', 'Tamil', 'Hindi', 'Telugu', 'Malayalam'])
    Jenre = SelectField(u'Select the Jenre', choices=['Action', 'Drama', 'Thriller', 'War/Military', 'Robbery', 'Comedy', 'Crime', 'Kids Friendly', 'Documentary', 'Animation'])


class MovieUpdate(FlaskForm):
    Update_Language = SelectField(u'Select the Language', choices=['English', 'Tamil', 'Hindi', 'Telugu', 'Malayalam'])
    Update_Jenre = SelectField(u'Select the Jenre', choices=['Action', 'Drama', 'Thriller', 'War/Military', 'Robbery', 'Comedy', 'Crime', 'Kids Friendly', 'Documentary', 'Animation'])
    Update_movie_name = TextField('Enter Movie Name:', validators=[DataRequired()])


movie_list = {

}

#To create a Table
class MovieTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Language = db.Column(db.String(50), nullable=False)
    Jenre = db.Column(db.String(50), nullable=False)
    MovieName = db.Column(db.String(50), unique=True, nullable=False)
    Rating = db.Column(db.Integer)
    MovieOverview = db.Column(db.Text(5000), nullable=False)
    ImageLocation = db.Column(db.Text(5000), nullable=False)


db.create_all()
db.session.commit()



@app.route('/home', methods=('GET', 'POST'))
def home():
    form = MovieUpdate()
    if form.validate_on_submit():
        #print(form.Update_Jenre.data)
        #movies_to_database = Movie(Language=form.Update_Language.data, Jenre=form.Update_Jenre.data, MovieName=form.Update_movie_name.data, Rating=form.Update_Rating.data)
        search = tmdb.Search()
        response = search.movie(query=form.Update_movie_name.data)
        try:
            movie_image = "https://image.tmdb.org/t/p/w500" + response['results'][0].get('backdrop_path')
            if movie_image == "None":
               movie_image = "https://image.tmdb.org/t/p/w500" + response['results'][0].get('poster_path')

        except:
            movie_image = "https://static.seattletimes.com/wp-content/uploads/2018/09/web-Careers-Career-Advice-Break-the-sorry-cycle-art-768x897.jpg"
        try:
            movie_overview = response['results'][0].get('overview')
        except:
            movie_overview = "Not Available"
        print(movie_overview)
        try:
            movie_rating = response['results'][0].get('vote_average')
        except:
            movie_rating = 0
        movies_to_database = MovieTable(Language=form.Update_Language.data, Jenre=form.Update_Jenre.data,
                                   MovieName=form.Update_movie_name.data, Rating=movie_rating, MovieOverview=movie_overview, ImageLocation=movie_image)
        print(movie_image, movie_overview)
        try:
            db.session.add(movies_to_database)
            db.session.commit()
            return render_template('completed.html')
        except:
            ram = "Movie already updated in Database"
            return render_template('home.html', form=form, ram=ram)

    return render_template('home.html', form=form)
@app.route('/firsthome', methods=('GET', 'POST'))
def submit():

    movie_list = []
    #movie_list2 = {}

    form = MyForm()
    if form.validate_on_submit():
        _selected_language = form.Language.data
        _selected_jenre = form.Jenre.data
        print(_selected_language)
        print(_selected_jenre)
        result = MovieTable.query.filter_by(Jenre=_selected_jenre, Language=_selected_language).all()
        print(result)
        index = 0
        try:
            while index < len(result):
                movie_list.append(result[index].MovieName)
                movie_list.append(result[index].MovieOverview)
                movie_list.append(result[index].Rating)
                movie_list.append(result[index].ImageLocation)
                index = index + 1
            print('MOVIE LIST',movie_list)
            matrix = [movie_list[i:i + 4] for i in range(0, len(movie_list), 4)]
            print('MOVIE LIST_MATRIX', matrix)
        except:
            print('Out of Range')
        return render_template('result1.html', movie_list=matrix, selected_language=_selected_language, selected_jenre=_selected_jenre)

    return render_template('index.html', form=form)

@app.route('/all_results', methods=('GET', 'POST'))
def all_results():

    print("hello")
    all_movies = MovieTable.query.all()
    print('results', all_movies)
    all_movies_results = []
    index = 0
    try:
        while index < len(all_movies):
            all_movies_results.append(all_movies[index].MovieName)
            print('first', all_movies_results)
            all_movies_results.append(all_movies[index].MovieOverview)
            print('Second', all_movies_results)
            all_movies_results.append(all_movies[index].Rating)
            all_movies_results.append(all_movies[index].ImageLocation)
            all_movies_results.append(all_movies[index].Jenre)
            all_movies_results.append(all_movies[index].Language)
            print('last', all_movies_results)

            #all_movies_results[all_movies[index].Jenre] = all_movies[index].MovieOverview
            index = index + 1
            print(all_movies_results)
        matrix1 = [all_movies_results[i:i + 6] for i in range(0, len(all_movies_results), 6)]
    except:
        print('Out of Range')
        return render_template('allresults.html', allmovies=matrix1)
    return render_template('allresults.html', allmovies=matrix1)


@app.route('/', methods=('GET', 'POST'))
def hello_world():
    return render_template('primary.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')


'''
Working COPY
'''
