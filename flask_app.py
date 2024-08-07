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
        doc_nrs = pd.DataFrame(data={'DocID': []})

    # Prefix with year
    prefix = "D" + str(datetime.now().year)[-2:]

    # Function to extract the numeric part after the prefix (with year)
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

        # All docnumbers of the current year
        docnrs_current_year = [int(get_digits(value)) for value in doc_nrs['DocID'] if value.startswith(prefix)]

        # Which numbers are used
        if 'button1' in request.form:

            # Check what the last added number is
            if len(docnrs_current_year) > 0: # or doc_nrs.empty for full list:
                # last_item = doc_nrs['DocID'].iloc[-1] # last entried
                if max(docnrs_current_year, default=None) != None:
                    last_item = "D" + str(max(docnrs_current_year, default=None)).zfill(3) # max number of this year
                    string = "t/m " + last_item + " is in gebruik voor dit jaar"
            else:
                string = "nog geen nummers zijn in gebruik voor dit jaar"

            return render_template('index.html', string=string)

        # New number
        elif 'button2' in request.form:

            # Check what the last added number is
            if len(docnrs_current_year) > 0:
                # last_item = doc_nrs['DocID'].iloc[-1]
                if max(docnrs_current_year, default=None) != None:
                    last_item = "D" + str(max(docnrs_current_year, default=None)).zfill(3)
                    nummer = extract_number(last_item) + 1
                    nummer_str = prefix + str(nummer).zfill(3)
                    string = "nieuw nummer: " + nummer_str

            else:
                last_item = None
                nummer_str = prefix + str(1).zfill(3) # make 1 --> 001
                string = "nieuw nummer: " + nummer_str

            # Append, save and return if number dont exist
            if nummer_str not in doc_nrs['DocID'].tolist():
                doc_nrs = doc_nrs.append({'DocID': nummer_str}, ignore_index=True)
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
