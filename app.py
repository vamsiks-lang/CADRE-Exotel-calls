from flask import Flask, request
from metabase_api import Metabase_API
from datetime import datetime

app = Flask(__name__)

# Your Metabase details
METABASE_URL = 'https://metabase.cadreodr.com'
METABASE_USERNAME = 'vamsi.ks@thecadre.in'
METABASE_PASSWORD = 'Universe123@#'
CARD_ID = 321  # Your saved card

mb = Metabase_API(METABASE_URL, email=METABASE_USERNAME, password=METABASE_PASSWORD)

@app.route('/exotel-message')
def get_message():
    phone = request.args.get('From')  # Phone from Exotel (clean it if needed)
    if phone.startswith('91'):
        phone = phone[2:]  # Remove country code for query if your DB stores 10 digits

    # Run Metabase query with phone parameter
    parameters = [
        {
            "type": "text",
            "target": ["variable", ["template-tag", "phone"]],
            "value": phone
        }
    ]
    results = mb.get_card_data(card_id=CARD_ID, data_format='json', parameters=parameters)

    if results and len(results) > 0:
        row = results[0]
        name = row.get('respondent_name', 'There')
        contract_id = row.get('contract_id')
        org = row.get('org_name', 'the concerned organization')
        client = row.get('client','online')
        meeting = row.get('meeting_type', 'hearing')
        try:
            event_raw = row['event_time'].split('.')[0]
            event_dt = datetime.strptime(event_raw, '%Y-%m-%d %H:%M:%S')
            event_text = event_dt.strftime('%d %B %Y at %I:%M %p').lstrip('0')
        except:
            event_text = 'tomorrow'

        # Build your exact dynamic sentence
        message = (f"Welcome to KADER ODR .............India's Simplest Online"
                   f" Dispute Resolution Platform.............."
                   f"Hello {name}, this is a reminder from CADRE ODR regarding your case {contract_id} "
                   f"for the organization {org}"
                   f"your {meeting} is scheduled on {event_text} on {client} platform."
                   f"Link regarding this case has already been shared to you via digital modes"
                   f"Kindly Attend the Meeting.")
    else:
        message = ("Hello, this is a reminder regarding your scheduled hearing tomorrow. Kindly Attend the meeting without fail.")

    return message  # Exotel gets this text and speaks it


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
