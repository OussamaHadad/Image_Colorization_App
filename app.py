from flask import Flask, render_template, request, redirect
import io
import base64
import os
from functions import *

app= Flask(__name__)

@app.route('/', methods= ['GET', 'POST'])
def colorize_image():
    if request.method == 'POST':
        # Image File Processing
        imagefile= request.files['imagefile']
        image_path= './images/'+ imagefile.filename
        imagefile.save(image_path)

        # Image array modification
        colored_img= pipeline(image_path)

        # Convert colored_img to base64
        buffered = io.BytesIO()
        colored_img.save(buffered, format="JPEG")  # Change format if needed
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        return render_template('index.html', prediction=f'<img src="data:image/jpeg;base64,{img_base64}" alt="Colorized Image">')
    else:
        return render_template('index.html', prediction='')
    
@app.route('/remove', methods=['POST'])
def remove_colorized_image():
    image_path = request.form.get('path')
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
    return redirect('/')  # Redirect back to the main page
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) #Define port so we can map container port to localhost
    app.run(host='0.0.0.0', port=port, debug= True)  #Define 0.0.0.0 for Docker
