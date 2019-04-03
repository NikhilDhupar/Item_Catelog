#!/usr/bin/env python3
# Python code for project item catalog
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book

engine = create_engine('sqlite:///bookstore.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/')
@app.route('/bookstore/')
def Hellobookstore():
    categorylist = session.query(Category).all()
    return render_template('categorylist.html', list=categorylist)


@app.route('/bookstore/<int:c_id>/')
def DisplayCategory(c_id):
    category = session.query(Category).filter_by(id=c_id).one()
    booklist = session.query(Book).filter_by(category_id=c_id)
    return render_template('displaybooks.html', category=category, list=booklist)

@app.route('/bookstore/addcategory/', methods=['GET', 'POST'])
def addcategory():
    if request.method == 'POST':
        newcategory = Category(name=request.form['name'])
        session.add(newcategory)
        session.commit()
        return redirect(url_for('Hellobookstore'))

    else:
        return render_template('newcategory.html')

@app.route('/bookstore/<int:c_id>/addbook/', methods=['GET', 'POST'])
def addbook(c_id):
    category = session.query(Category).filter_by(id=c_id).one()
    if request.method == 'POST':
        print("Inside post of addbook")
        newbooks=Book(name=request.form['name'],price=request.form['price'],author=request.form['author'],description=request.form['description'],category_id=c_id)
        session.add(newbooks)
        session.commit()
        return redirect(url_for('DisplayCategory',c_id=c_id) )
    else:
        return render_template('newbook.html',category=category)


@app.route('/bookstore/<int:c_id>/delbook/<int:b_id>')


@app.route('/bookstore/delcategory/<int:c_id>', methods=['GET', 'POST'])
def deletecategory(c_id):
    item = session.query(Category).filter_by(id=c_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('Hellobookstore'))
    else:
        return render_template('deletecategory.html', category=item)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
