from flask import Flask, render_template, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
import requests
import openai
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
openai.api_key = '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'


db = SQLAlchemy(app)
app.app_context().push()


class Responses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    goal = db.Column(db.String(500))
    commitment = db.Column(db.String(50))
    diet = db.Column(db.String(50))


app.config['OPENAI_API_KEY'] = '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'


@app.route("/")
def home():
    return render_template('index.html')
@app.route("/questionare", methods=['GET','POST'])
def questionare():
    if request.method == "POST":
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        goal = request.form['goal']
        commitment = request.form['commitment']
        diet = request.form['diet']
        responses = Responses(age=age, weight=weight, height=height, goal=goal, commitment=commitment, diet=diet)
        db.session.add(responses)
        db.session.commit() 
        return redirect(url_for('workouts'))
    return render_template("questionare.html")
@app.route("/workouts")
def workouts():
    latest_response = Responses.query.order_by(Responses.id.desc()).first()
    prompt = f"Generate a daily workout routine to follow for a person with age {latest_response.age}, weight {latest_response.weight}, height {latest_response.height}, goal {latest_response.goal}, diet {latest_response.diet}, and time commitment {latest_response.commitment}"
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": prompt},
        ]
    )
    generated_text = openai_response['choices'][0]['message']['content']
    items = generated_text.split('\n')

    html_output = '<ul id="ogList">'
    for item in items:
        if item: 
            if '**' in item:  
                html_output += f'<li><strong>{item.replace("**", "")}</strong></li>'
            else:
                html_output += f'<li>{item}</li>'
    html_output += '</ul>'
    return render_template('workouts.html', workout=html_output)
@app.route("/timer")
def timer():
    return render_template("timer.html")
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)



