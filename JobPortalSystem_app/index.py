from flask import Flask, render_template

app = Flask(__name__)
@app.route('/JobPortalSystem')
@app.route('/')

def index():
    return "<h1>Welcome to Job Portal System!!!</h1>"

if __name__ == '__main__':
    app.run(debug=True)