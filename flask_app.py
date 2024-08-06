from flask import Flask, request, render_template, Response
import pandas as pd
import os, re
from datetime import datetime
# from io import StringIO, BytesIO
# from werkzeug.wsgi import FileWrapper

# Flask constructor
app = Flask(__name__)

# Root endpoint
@app.route('/', methods=['GET', 'POST'])
def index():

    # Load dataframe with IDs
    if os.path.isfile('mysite/docnummers/docnummers.csv'):
        doc_nrs = pd.read_csv('mysite/docnummers/docnummers.csv', sep=";")
    else:
        doc_nrs = pd.DataFrame(data={'ID': []})

    # Prefix
    prefix = "D" + str(datetime.now().year)[-2:]

    # Function to extract the numeric part after the prefix
    def extract_number(input_string):
        # return int(input_string.replace(prefix, ""))
        match = re.search(r'{}(\d+)'.format(prefix), input_string)
        if match:
            return int(match.group(1))
        else:
            return 0

    # Function to get digits only from numbers
    def get_digits(value):
        digits = re.findall(r'\d+', value)
        return ''.join(digits)

    # User input
    if request.method == 'POST':

        # Which numbers are used
        if 'button1' in request.form:

            # Check what the last added number is
            if not doc_nrs.empty:
                # last_item = doc_nrs['ID'].iloc[-1] # last entried
                # last_item = sorted(doc_nrs['ID'].astype(str).tolist())[-1] # continu with chronological last number
                last_item = "D" + str(max([int(get_digits(value)) for value in doc_nrs['ID'] if value.startswith(prefix)])).zfill(3) # max number of this year
                string = "t/m " + last_item + " is in gebruik voor dit jaar"
            else:
                string = "nog geen nummers zijn in gebruik"

            return render_template('index.html', string=string)

        # New number
        elif 'button2' in request.form:

            # Check what the last added number is
            if not doc_nrs.empty:
                # last_item = doc_nrs['ID'].iloc[-1]
                # last_item = sorted(doc_nrs['ID'].astype(str).tolist())[-1] # continu with chronological last number
                last_item = "D" + str(max([int(get_digits(value)) for value in doc_nrs['ID'] if value.startswith(prefix)])).zfill(3)

                # Check if you are in new year, then start with str(1).zfill(3)
                if last_item.startswith(prefix): # same year
                    nummer = extract_number(last_item) + 1
                    nummer_str = prefix + str(nummer).zfill(3)
                    string = "nieuw nummer: " + nummer_str
                else: # new year
                    nummer_str = prefix + str(1).zfill(3) # --> 001
                    string = "nieuw nummer: " + nummer_str

            else:
                last_item = None
                nummer_str = prefix + str(1).zfill(3) # make 1 --> 001
                string = "nieuw nummer: " + nummer_str

            # Append, save and return if number dont exist
            if nummer_str not in doc_nrs['ID'].tolist():
                doc_nrs = doc_nrs.append({'ID': nummer_str}, ignore_index=True)
                doc_nrs.to_csv('mysite/docnummers/docnummers.csv', sep=";", index=False)
            else:
                string = "nummer bestaat al: " + nummer_str

            return render_template('index.html', string=string)

        # Download
        elif 'button3' in request.form:

            # Load dataframe as CSV and create Flask Response
            csv_data = doc_nrs.to_csv(index=False, encoding='utf-8', sep=";")
            response =  Response(csv_data,mimetype='text/csv')

            # Return with filename
            filename = "docnummers_" + str(datetime.now().year) + str(datetime.now().month).zfill(2) + str(datetime.now().day).zfill(2) + ".csv"
            filename = filename.replace(" ", "")
            response.headers.set("Content-Disposition", "attachment", filename=filename)
            return response


    # Display the HTML form template with no input
    return render_template('index.html', string=None)

# Main Driver Function
if __name__ == '__main__':
    app.run()
