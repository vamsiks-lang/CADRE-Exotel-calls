from flask import Flask, request, Response
from datetime import datetime

app = Flask(__name__)

# === YOUR REAL METABASE DETAILS HERE ===
METABASE_URL = 'https://metabase.cadreodr.com'
METABASE_USERNAME = 'vamsi.ks@thecadre.in'
METABASE_PASSWORD = 'Universe123@#'  # Your actual password
CARD_ID = 321
# ======================================

@app.route('/exotel-message', methods=['GET'])
def get_message():
    phone = request.args.get('From')

    if not phone:
        default_msg = "Hello, this is a reminder regarding your scheduled hearing. Please attend without fail."
        return Response(default_msg, mimetype='text/plain')

    # Clean phone number
    phone = phone.strip().lstrip('+')
    if phone.startswith('91') and len(phone) > 10:
        phone = phone[2:]  # Keep only 10 digits

    # Lazy load: Import and connect to Metabase ONLY when needed
    try:
        from metabase_api import Metabase_API
        mb = Metabase_API(METABASE_URL, email=METABASE_USERNAME, password=METABASE_PASSWORD)

        parameters = [
            {
                "type": "text",
                "target": ["variable", ["template-tag", "phone"]],
                "value": phone
            }
        ]

        results = mb.get_card_data(card_id=CARD_ID, data_format='json', parameters=parameters)
    except Exception as e:
        print(f"Metabase error: {e}")
        results = []

    # Build message
    if results and len(results) > 0:
        row = results[0]
        name = row.get('respondent_name', 'there').strip()
        contract_id = row.get('contract_id', 'your case')
        org = row.get('org_name', 'the concerned organization')
        client = row.get('client', 'online')
        meeting = row.get('meeting_type', 'hearing')

        try:
            event_raw = row['event_time'].split('.')[0]
            event_dt = datetime.strptime(event_raw, '%Y-%m-%d %H:%M:%S')
            event_text = event_dt.strftime('%d %B %Y at %I:%M %p').lstrip('0').replace(' 0', ' ')
        except:
            event_text = 'tomorrow'

        message = (
            "Welcome to CADRE ODR, India's Simplest Online Dispute Resolution Platform. "
            f"Hello {name}, this is a reminder regarding your case {contract_id} with {org}. "
            f"Your {meeting} is scheduled on {event_text} on the {client} platform. "
            "Information regarding this has already been sent to you via digital modes. "
            "Kindly attend the meeting without fail. Thank you."
        )
    else:
        message = (
            "Hello, this is an automated reminder from CADRE ODR "
            "regarding your upcoming scheduled hearing. "
            "Please ensure you attend the meeting without fail. Thank you."
        )

    return Response(message, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
