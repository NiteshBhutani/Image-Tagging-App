import os
import json,unicodedata
from flask import Flask,render_template,request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from clarifai.client import ClarifaiApi

#Calrifai Client id and client secret
clientid = os.getenv(CLARIFAI_ID);
clientsecret = os.getenv(CLARIFAI_SECRET);

clarifai_api = ClarifaiApi(clientid,clientsecret) # assumes environment variables are set.
#creating the app
app= Flask(__name__)

# This is the path to the upload directory where images would be saved.
app.config['UPLOAD_FOLDER'] = 'Templates/'


app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Route that will process the file upload
@app.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        # Check file extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try :
                result = clarifai_api.tag_images(open('/home/nitesh/Documents/image_predictor/'+os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb'))
            except Exception :
                print "Not able to predict the image!!"
            
            prediction_result = retrieve_result(result)
            return redirect(url_for('uploaded_file', filename=filename,result=prediction_result))
    return redirect(url_for('main'))
    
        
#Route to send images from Upload folder as response to incoming request
@app.route('/uploads/<filename>')
def sendfile_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
#Route to send the result
@app.route('/<filename>')
def uploaded_file(filename):
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    if filename != None :
        return render_template('index.html', url=filename,result=request.args.get('result'))
    else :
        return "Upload not successfull"



#Parse Json - TODO- Need to add more checks - for better parsing
def retrieve_result(result):
    prediction_result=None
    if((unicodedata.normalize('NFKD', result['status_code']).encode('ascii','ignore')) == 'OK' or (unicodedata.normalize('NFKD', result['status_code']).encode('ascii','ignore')) == 'PARTIAL_ERROR') :
        prediction_result=result['results'][0]['result']['tag']['classes'][0]
        
    return (unicodedata.normalize('NFKD', prediction_result).encode('ascii','ignore'))


@app.route("/")
def main():
    return render_template('index.html')



if __name__ == "__main__":
    app.run()
