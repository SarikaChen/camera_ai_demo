import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from inference import run_super_resolution, run_denoise

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
RESULT_FOLDER = os.path.join(APP_ROOT, 'results')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.secret_key = 'changeme-secret'  # for flash messages

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            mode = request.form.get('mode', 'sr')
            filename = secure_filename(file.filename)
            in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(in_path)

            base, ext = os.path.splitext(filename)
            out_name = f"{base}_{mode}{ext}"
            out_path = os.path.join(app.config['RESULT_FOLDER'], out_name)

            try:
                if mode == 'sr':
                    run_super_resolution(in_path, out_path)
                else:
                    run_denoise(in_path, out_path)
            except Exception as e:
                flash(f'Processing failed: {e}')
                return redirect(request.url)

            return redirect(url_for('result', orig=filename, proc=out_name))
        else:
            flash('File type not allowed. Use png/jpg/jpeg/bmp.')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/results/<path:filename>')
def results_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

@app.route('/uploads/<path:filename>')
def uploads_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/result', methods=['GET', 'POST'])
def result():
    # 如果誤送 POST 到 /result，就導回首頁
    if request.method == 'POST':
        return redirect(url_for('index'))
    orig = request.args.get('orig')
    proc = request.args.get('proc')
    if not orig or not proc:
        return redirect(url_for('index'))
    return render_template('index.html', orig=orig, proc=proc)

if __name__ == '__main__':
    # For demo use only
    app.run(host='127.0.0.1', port=5000, debug=True)