import json
from flask import Flask, render_template, request, redirect, url_for, jsonify,send_from_directory
from model_code import extract_text_from_pdf, run_rag_pipeline, process_output
from tempfile import NamedTemporaryFile
import os
objs=[]
global_username=''
app = Flask(__name__)

@app.route('/data/<path:path>')
def static_file(path):
    file_path = os.path.join('data', path)
    if os.path.exists(file_path):
        return send_from_directory('data', path)
    else:
        return 'File not found', 404
    
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/sme_login')
def sme_login():
    return render_template('sme_login.html')

@app.route('/sme_homepage')
def sme_homepage():
    username = request.args.get('name', '') 
    global global_username
    global_username = username
    return render_template('sme_homepage.html', username=global_username)

@app.route('/admin_homepage')
def admin_homepage():
    return render_template('admin_homepage.html')

@app.route('/upload_page')
def upload_page(): 
    return render_template('upload_doc.html')

@app.route('/upload_forview')
def upload_forview(): 
    return render_template('upload_forview.html')

@app.route('/feedback_page')
def feedback_page():
    global global_username
    task_value = request.args.get('task', '') 
    return render_template('feedback.html', username=global_username,task=task_value)

@app.route('/feedback_data')
def feedback_data():
    with open('C:\\pppppppp\\data\\feedback_data.json', 'r') as file:
        feedback_data = json.load(file)
    return jsonify(feedback_data)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback_data = request.json  
    try:
        with open('feedback_data.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []
    existing_data.append(feedback_data)
    with open('feedback_data.json', 'w') as file:
        json.dump(existing_data, file, indent=4)
    return redirect(url_for('mvo_contentgen_page')) 


@app.route('/uploadview', methods=['POST'])
def uploadview():
    if 'document' not in request.files:
        return "No file part"
    file = request.files['document']
    if file.filename == '':
        return "No selected file"
    filename = file.filename
    return render_template('view.html', filename=filename)


@app.route('/content_data')
def content_data():
    with open('C:\pppppppp\data\content_data.json', 'r') as file:
        feedback_data = json.load(file)
    return jsonify(feedback_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    global objs
    if 'document' not in request.files:
        return "No file part"
    file = request.files['document']
    if file.filename == '':
        return "No selected file"
    #temp_file = NamedTemporaryFile(delete=False)
    #file.save(temp_file)
    #temp_file.close()  
    #file_path = temp_file.name
    #doc = extract_text_from_pdf(file_path)
    #docs=[]
    #docs.append(doc)
    #obj=run_rag_pipeline(docs)
    #objs.append(obj)
    return '''
        <script>
            alert("File uploaded successfully!");
            window.location.href = '/mvo_contentgen_page';
        </script>
    '''

@app.route('/mvo_contentgen_page')
def mvo_contentgen_page():
    return render_template('content_gen.html')

@app.route('/get_learning_goal')
def get_learning_goal():
    global objs 
    if objs not in objs:
        return jsonify(data="error: Upload document again")
    query="consider the given text as raw text and as a instruction designer write the learning goal of the raw text and learning goal should cover all the raw text"
    learning_goal_data = process_output(objs[0],query)  
    print(learning_goal_data)
    return jsonify(data=learning_goal_data)

@app.route('/getlearning_outcomes')
def getlearning_outcomes():
    global objs 
    if objs not in objs:
        return jsonify(data="error: Upload document again")
    query="consider the given text as raw text and as a instruction designer write the learning outcomes of the raw text and learning outcomes should be in points of numbers"
    learning_goal_data = process_output(objs[0],query)  
    print(learning_goal_data)
    return jsonify(data=learning_goal_data)


@app.route('/getlearning_content')
def getlearning_content():
    global objs 
    if objs not in objs:
        return jsonify(data="error: Upload document again")
    query="consider the given text as raw text and as a instruction designer provide the learning content of the raw text for 3 learning outcomes with detail explanation should be in points of numbers"
    learning_goal_data = process_output(objs[0],query)  
    print(learning_goal_data)
    return jsonify(data=learning_goal_data)


@app.route('/assessment_page')
def assessment_page(): 
    return render_template('assessment.html')

@app.route('/assessment')
def assessment():
    global objs 
    if objs not in objs:
        return jsonify(data="error: Upload document again")
    query="consider the given text as raw text and as a instruction designer provide the learning content of the raw text for 3 learning outcomes with detail explanation should be in points of numbers"
    learning_goal_data = process_output(objs[0],query)  
    print(learning_goal_data)
    return jsonify(data=learning_goal_data)


@app.route('/chat_page')
def chat_page(): 
    return render_template('chat.html')


if __name__ == '__main__':
    app.run(debug=True)
