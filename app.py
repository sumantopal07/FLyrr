import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from datetime import datetime, timedelta
from forms import *
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
migrate=Migrate(app,db)
managar=Manager(app)
managar.add_command('db',MigrateCommand)
#=================VENUE===================#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    city = db.Column(db.String(500))
    state = db.Column(db.String(500))
    address = db.Column(db.String(500))
    phone = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    show_relation1=db.relationship('Shows',backref='Venue_Owner',lazy=True)

#=================ARITST==================#
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    city = db.Column(db.String(500))
    state = db.Column(db.String(500))
    phone = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    show_relation2=db.relationship('Shows',backref='Artist_Owner',lazy=True)
    def __repr__(self):
        return str({'ID': {self.id} ,'name' :{self.name}})
    def __init__(self, name, genres, city, state, phone,facebook_link, image_link):
      self.name = name
      self.genres = genres
      self.city = city
      self.state = state
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link

#=================SHOWS==================#
class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
    date_time = db.Column(db.DateTime, nullable=False)
    def __init__(self, artist_id, venue_id, date_time):
      self.artist_id = artist_id
      self.venue_id = venue_id
      self.date_time = date_time
    def __repr__(self):
        return str({'ID': {self.id} ,'name' :{self.artist_id}})

# db.drop_all()
db.create_all()

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

# app.jinja_env.filters['datetime'] = format_datetime

#============HOME PAGE================#
@app.route('/')
def index():
  return render_template('pages/home.html')


@app.route('/venues')
#============VENUE GET================#/////
def venues():
  var=Venue.query.all()
  dict={}#(city,name)->list(id,name)
  for i in var:
    key=tuple([i.city,i.state])
    value=[i.id,i.name]
    if key in dict:
      dict[key].append(value)
    else:
      dict[key]=[]
      dict[key].append(value)
  return render_template('pages/venues.html', areas=dict)

#============VENUE SEARCH================#
@app.route('/venues/search', methods=['POST'])
def search_venues():
  s=request.form.get('search_term', '')
  dict=Venue.query.filter(Venue.name.ilike("%"+s+"%")).all()
  return render_template('pages/search_venues.html', results=dict, search_term=request.form.get('search_term', ''))

#============VENUE_ID================#
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  dict=Venue.query.filter_by(id=venue_id).all()
  if len(dict)==0:
    return render_template('errors/404.html'), 404
  dict=dict[0]
  GENRES=Venue.query.filter_by(id=venue_id).one().genres[1:-2].split(',')
  temp=Shows.query.filter_by(venue_id=venue_id).all()
  upcoming,past=[],[]
  now=format_datetime(datetime.now(),'full')
  for i in temp:
    date=format_datetime(i.date_time,'full')
    if(now>date):
      past.append([i,Artist.query.filter_by(id=i.artist_id).all()[0].image_link,Artist.query.filter_by(id=i.artist_id).all()[0].name,format_datetime(i.date_time,'full')])
    else:
      upcoming.append([i,Artist.query.filter_by(id=i.artist_id).all()[0].image_link,Artist.query.filter_by(id=i.artist_id).all()[0].name,format_datetime(i.date_time,'full')])
  data=[dict,past,upcoming,GENRES]
  return render_template('pages/show_venue.html', obj=data)
  

#============VENUE CREATE_FORM================#
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


#============VENUE POST================#
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  address = form.address.data
  facebook_link = form.facebook_link.data
  image_link = form.image_link.data
  try:
    venue = Venue(name=name, city=city, state=state, phone=phone,
                        genres=genres, facebook_link=facebook_link, 
                        image_link=image_link,address=address)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#============ARTIST GET================#
@app.route('/artists')
def artists():
  var=Artist.query.all()
  return render_template('pages/artists.html', var=var)

#============ARTIST SEARCH================#
@app.route('/artists/search', methods=['POST'])
def search_artists():
  s=request.form.get('search_term', '')
  dict=Artist.query.filter(Artist.name.ilike("%"+s+"%")).all()
  return render_template('pages/search_artists.html', results=dict, search_term=request.form.get('search_term', ''))
  
#============ARTIST_ID================#
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  dict=Artist.query.filter_by(id=artist_id).all()
  if len(dict)==0:
    return render_template('errors/404.html'), 404
  dict=dict[0]
  GENRES=Artist.query.filter_by(id=artist_id).one().genres[1:-2].split(',')
  temp=Shows.query.filter_by(artist_id=artist_id).all()
  upcoming,past=[],[]
  now=format_datetime(datetime.now(),'full')
  for i in temp:
    date=format_datetime(i.date_time,'full')
    if(now>date):
      past.append([i,Venue.query.filter_by(id=i.venue_id).all()[0].image_link,Venue.query.filter_by(id=i.venue_id).all()[0].name,format_datetime(i.date_time,'full')])
    else:
      upcoming.append([i,Venue.query.filter_by(id=i.venue_id).all()[0].image_link,Venue.query.filter_by(id=i.venue_id).all()[0].name,format_datetime(i.date_time,'full')])
  # print(upcoming[0][0].start_time)
  data=[dict,past,upcoming,GENRES]
  return render_template('pages/show_artist.html', obj=data)

#=================ARITST FORM CREATE==================#
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form=ArtistForm()
  return render_template('forms/new_artist.html', form=form)

#============ARTIST POST================#
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  facebook_link = form.facebook_link.data
  image_link = form.image_link.data
  try:
    artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres, facebook_link=facebook_link, 
                        image_link=image_link)
    # artist = Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],phone=request.form('phone'),facebook_link=request.form['facebook_link'],image_link=request.form['image_link'])
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    flash('Aritst ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

#============SHOWS GET================#
@app.route('/shows')
def shows():
  data=Shows.query.order_by(Shows.date_time<datetime.utcnow()).all()
  DATA=[]
  for i in data:
    temp=[]
    temp.append(format_datetime(i.date_time,'full'))
    temp.append(i.artist_id)
    temp.append(i.venue_id)
    temp.append(Artist.query.filter_by(id=i.artist_id).first().name)
    temp.append(Venue.query.filter_by(id=i.venue_id).first().name)
    temp.append(Artist.query.filter_by(id=i.artist_id).first().image_link)
    DATA.append(temp)
  return render_template('pages/shows.html', shows=DATA)

#============SHOWS CREATE================#
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


#============SHOW POST================#
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm()
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    artist_id = form.artist_id.data
    show=Shows(artist_id, venue_id,start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#============EDIT ARTIST GET================#
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  dict=Artist.query.filter_by(id=artist_id).all()
  if len(dict)==0:
    return render_template('errors/404.html'), 404
  dict=dict[0]
  return render_template('forms/edit_artist.html', form=form, artist=dict)

#============EDIT ARTIST POST================#
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],address=request.form['address'],phone=request.form('phone'),genres=request.form['genres'],facebook_link=request.form['facebook_link'])
    x = Artist.query.filter_by(id=artist.id).first()
    x.name =request.form['name']
    x.city =request.form['city']
    x.state=request.form['state']
    x.address=request.form['address']
    x.phone=request.form('phone')
    x.genres=request.form['genres']
    x.facebook_link=request.form['facebook_link']
    x.image_link=request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    flash('Artist ' + request.form['name'] + ' was edited successfully!')
  return redirect(url_for('show_artist', artist_id=artist_id))

#============EDIT VENUE GET================#
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  dict=Venue.query.filter_by(id=venue_id).all()
  if len(dict)==0:
    return render_template('errors/404.html'), 404
  dict=dict[0]
  return render_template('forms/edit_venue.html', form=form, venue=dict)

#============EDIT VENUE POST================#
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    #venue = Venue(name=request.form['name'],city=request.form['city'],state=request.form['state'],address=request.form['address'],phone=request.form('phone'),genres=request.form['genres'],facebook_link=request.form['facebook_link'])
    x = Venue.query.filter_by(id=venue_id).first()
    x.name =request.form['name']
    x.city =request.form['city']
    x.state=request.form['state']
    x.address=request.form['address']
    x.phone=request.form('phone')
    x.genres=request.form['genres']
    x.facebook_link=request.form['facebook_link']
    x.image_link=request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    flash('Venue ' + request.form['name'] + ' was edited successfully!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#============VENUE DELETE================#
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id): 
  obj = Venue.query.filter_by(id=venue_id).all()
  if(len(obj)==0):
    flash('Does\'nt exist')
  else:
    db.session.delete(obj[0])
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('home.html')

#============404================#
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

#============500================#
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
  
if __name__ == '__main__':
    app.run()
# Or specify port manually:
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5100))
#     app.run(host='0.0.0.0', port=port)