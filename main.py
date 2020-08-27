import sys
sys.path.append('./data builder')
import database_getter, calendar_getter
from control_flow import main_search, current_mode, get_context
from datetime import datetime
from flask import Flask, render_template, request

TEMPLATES_AUTO_RELOAD = True
app = Flask(__name__)
#
# uid = "1"


import pickle
with open("temp.txt","rb") as f:
    recommendations = pickle.load(f)

@app.route('/<uid>')
def homepage(uid):
    return render_template('dashboard.html',
                           uid=uid,
                           home_address=database_getter.get_user_home_address(uid),
                           school_address=database_getter.get_user_school_address(uid),
                           work_address=database_getter.get_user_work_address(uid),
                           current_steps=database_getter.get_user_current_step(uid),
                           current_time=datetime.now(),
                           upcoming_events=calendar_getter.get_calendar_events_list(uid,datetime.now()))

@app.route('/rec/<uid>')
def rec_page(uid):
    context = get_context(uid=uid,
                            current_steps=database_getter.get_user_current_step(uid),
                            current_location="400 W Disney Way, Anaheim, CA 92802",
                            #current_location=database_getter.get_user_home_address(uid),
                            current_time=datetime.now())
    return render_template('recommendation.html',
                            uid=uid,
                            #rec_mode= current_mode(uid,datetime(year=2020,month=3,day=18,hour=23)),
                            rec_mode=current_mode(uid,datetime.now()),
                            event_location=context[2],
                            event_time=context[3],
                            spare_time=context[4],
                            travel_mode=context[6],
                            events=context[5],
                            ideal_distance=context[1])

@app.route('/options/<uid>')
def options(uid):
    recommendations = main_search(
                        uid,
                        database_getter.get_user_current_step(uid),
                        database_getter.get_user_current_location(uid),
                        datetime.now())
    return render_template('options.html',
                        uid=uid,
                        recommendations=recommendations)

@app.route('/trip/<uid>',methods=['POST','GET'])
def trip(uid):
    if request.method == 'POST':
        option = request.form['rec']
    else:
        option='not selected'
    return render_template('trip.html',
                        uid=uid,
                        option=option)


if __name__ == '__main__':
    app.run(debug=True)
