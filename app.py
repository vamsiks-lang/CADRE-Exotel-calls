from flask import Flask, request, Response
import re

app = Flask(__name__)

# === YOUR REAL METABASE DETAILS HERE ===
METABASE_URL = 'https://metabase.cadreodr.com'
METABASE_USERNAME = 'vamsi.ks@thecadre.in'
METABASE_PASSWORD = 'Universe123@#'  # Your actual password
CARD_ID = 321
# ======================================

@app.route('/exotel-message', methods=['GET'])
def get_message():
    phone = request.args.get('From').strip()

    if not phone:
        default_msg = "Hello, this is a reminder regarding your scheduled hearing. Please attend without fail."
        return Response(default_msg, mimetype='text/plain')

    # Clean phone number
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 12 and phone.startswith('91'):
        phone = phone[2:]

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
        return Response(
            f"Metabase error: {e}",
            status=500,
            mimetype='text/plain'
        )

    # Build message
    if results and len(results) > 0:
        row = results[0]
        name = (row.get('respondent_name') or 'there').strip()
        contract_id = row.get('contract_id', 'your case')
        org = row.get('org_name', 'the concerned organization')
        client = row.get('client', 'online')
        meeting = row.get('meeting_type', 'hearing')
        event_text = row.get('event_time', 'tomorrow')

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
