# app/main/routes.py
import os
from flask import render_template, request, flash, redirect, url_for, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import bp
from .utils import process_uploaded_file, check_artifacts # Import processing logic

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # Check if artifacts are loaded before allowing upload attempt
    if not check_artifacts():
         flash('Prediction service is currently unavailable due to configuration issues. Please contact support.', 'danger')
         # Render index but maybe disable the form visually or just show the error
         return render_template('main/index.html', service_unavailable=True)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part selected.', 'warning')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                # Ensure upload folder exists just before saving
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                print(f"File saved to {filepath}")

                # Process the file using the utility function
                fraud_list, summary_data = process_uploaded_file(filepath)

                # Store results in session to pass to dashboard route
                session['analysis_results'] = {
                    'fraud_list': fraud_list,
                    'summary': summary_data
                }
                session['original_filename'] = filename # Store filename for display

                # Optionally remove the file after processing
                # try:
                #     os.remove(filepath)
                #     print(f"Removed uploaded file: {filepath}")
                # except OSError as e:
                #     print(f"Error removing file {filepath}: {e}")

                flash(f'File "{filename}" processed successfully!', 'success')
                return redirect(url_for('main.dashboard'))

            except (ValueError, RuntimeError, FileNotFoundError) as e:
                print(f"Route Error: {e}")
                flash(f"Error processing file: {e}", 'danger')
                # Clean up file if processing failed
                if os.path.exists(filepath):
                     try: os.remove(filepath)
                     except OSError as re: print(f"Error removing file {filepath} after error: {re}")
                return redirect(request.url) # Redirect back to upload page on error
            except Exception as e:
                print(f"Unexpected Route Error: {type(e).__name__} - {e}")
                import traceback
                traceback.print_exc()
                flash(f"An unexpected error occurred during processing: {type(e).__name__}.", 'danger')
                if os.path.exists(filepath):
                    try: os.remove(filepath)
                    except OSError as re: print(f"Error removing file {filepath} after error: {re}")
                return redirect(request.url)

        else:
            flash('Invalid file type. Only CSV files are allowed.', 'warning')
            return redirect(request.url)

    # GET request
    return render_template('main/index.html', title='Upload Transactions', service_unavailable=False)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Retrieve results from session
    results = session.get('analysis_results', None)
    filename = session.get('original_filename', 'N/A')

    if results is None:
        flash('No analysis results found. Please upload a file first.', 'info')
        return redirect(url_for('main.index'))

    # Clear the session data after retrieving it (optional, prevents re-display on refresh)
    # session.pop('analysis_results', None)
    # session.pop('original_filename', None)


    return render_template('main/dashboard.html',
                           title='Analysis Dashboard',
                           filename=filename,
                           fraudulent_transactions=results.get('fraud_list', []),
                           summary=results.get('summary', {}))