from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import nagg_oo


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

#class ReusableForm(Form):
#    name = TextField('Name:', validators=[validators.required()])


# Recommender initializations
RS = nagg_oo.rec_server()

# recommended career - output format mapping
def clean_careers(rc):
    cmap = {'management_consultant' : 'Management Consultant',
        'investment_banker' : 'Investment Banker',
        'ad_executive' : 'Advertising Executive'}
    output = []
    for c in rc:
        output.append(cmap[c[0]])
    return output

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name=request.form['name']
        
        if name[0]=='@':
            user_statuses = RS.user_twitter(name)
            print('{}'.format(user_statuses))
            user_sample_article = RS.user_input([user_statuses])
            user_sample_career = RS.user_input([user_statuses], rtype='career')
        else:
            user_sample_article = RS.user_input([name])
            user_sample_career = RS.user_input([name],rtype='career')
        
        
        #recommend articles
        #user_sample = RS.user_input([user_statuses])
        articles = RS.recommend_articles(user_sample_article, 3)

        #recommend career
        #user_sample = RS.user_input([user_statuses], rtype='career')
        recommended_careers = RS.recommend_careers(user_sample_career, 3)
        clean_rc = clean_careers(recommended_careers)
        
        job_info = []
        for career in recommended_careers:
            job_info.append(RS.job_infosource[career[0]])
        
        #return redirect(url_for('static', filename='career_results/wizard.html'))
        return render_template('results_jinja.html', articles=articles, careers=clean_rc, job_info=job_info) #make the results template dependent on the returned values

    return render_template('index.html', form=request.form)

if __name__ == "__main__":
    app.run()
