'''Language Selector

This Flask app replicates the behavior of a PHP app assigned (due) 04/03/24 in CSCI 284 (Drinen). The app
is to display a drop-down menu containing the names of some number of countries, then when the button is clicked, a
new page displays the languages spoken in that country. The list of countries is to come from the database table
spring25_cs284::world_x_country.'''

import myid # type: ignore
from flask import Flask, render_template, redirect, url_for, request # type: ignore
from flask_bootstrap import Bootstrap5 # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.sql import text # type: ignore
from sqlalchemy import desc # type: ignore

from flask_wtf import FlaskForm, CSRFProtect # type: ignore
from wtforms import BooleanField, SelectField, SubmitField # type: ignore

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'tO$&!|0wkamvVia0?n$NqI'

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = myid.userpass + myid.server + myid.dbname
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy()
db.init_app(app)

class Country(db.Model):
    __tablename__ = 'world_x_country'
    code = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    capital = db.Column(db.Integer)
    code2 = db.Column(db.String)

class Language(db.Model):
    __tablename__ = 'world_x_country_language'
    CountryCode = db.Column(db.String, primary_key=True)
    Language = db.Column(db.String, primary_key=True)
    IsOfficial = db.Column(db.String)
    Percentage = db.Column(db.Float)

class LForm(FlaskForm):
     clist = SelectField('Please select a country: ', choices=[])
     official = BooleanField('Include only official languages')
     submit = SubmitField('View Languages')


@app.route('/', methods=['GET', 'POST'])
def select():
    countries = []

    try:
        country = db.session.execute(db.select(Country)
                                               .order_by(Country.name)).scalars()
        for c in country:
            countries.append((c.code, c.name))

        form = LForm()
        form.clist.choices = countries
        if form.validate_on_submit():
            cc = form.clist.data
            if cc == '':
                cc = 'SWE'
            off  = form.official.data
            return redirect('languages/' + cc + '/' + str(off))
        return render_template('index.html', form=form)

    except Exception as e:
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

## SHOULD NEVER EXECUTE THIS ROUTE - DEBUG ONLY
@app.route('/languages')
def oops():
    return '<h1>No Language Selected</h2>'

@app.route('/languages/<cc>/<off>')
def languages(cc, off):
    try:
        languages = db.session.execute(db.select(Language)
                                        .filter_by(CountryCode=cc)
                                        .order_by(desc(Language.Percentage))).scalars()
        
        return render_template('languages.html', langs=languages, off=off)

    except Exception as e:
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
