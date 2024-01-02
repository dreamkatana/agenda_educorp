from flask import Flask, render_template
from flask_talisman import Talisman
import requests
from icalendar import Calendar
from datetime import datetime, timedelta
import pytz
from itertools import groupby

app = Flask(__name__)
Talisman(app)

def fetch_ics(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_ics(ics_content):
    calendar = Calendar.from_ical(ics_content)
    events = []
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    for component in calendar.walk('vevent'):
        dtstart = component.get('dtstart').dt
        dtend = component.get('dtend').dt

        # Convert to local time zone if datetime is timezone-aware (UTC)
        if isinstance(dtstart, datetime) and dtstart.tzinfo is not None and dtstart.tzinfo.utcoffset(dtstart) is not None:
            dtstart = dtstart.astimezone(sao_paulo_tz)
        elif not isinstance(dtstart, datetime):
            # Combine date with minimum time and localize to Sao Paulo timezone
            dtstart = sao_paulo_tz.localize(datetime.combine(dtstart, datetime.min.time()))

        if isinstance(dtend, datetime) and dtend.tzinfo is not None and dtend.tzinfo.utcoffset(dtend) is not None:
            dtend = dtend.astimezone(sao_paulo_tz)
        elif not isinstance(dtend, datetime):
            # Combine date with minimum time and localize to Sao Paulo timezone
            dtend = sao_paulo_tz.localize(datetime.combine(dtend, datetime.min.time()))

        events.append({
            'summary': str(component.get('summary')),
            'start': dtstart,
            'end': dtend
        })
    return events

def filter_current_events(events):
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    return [event for event in events if event['start'] <= now <= event['end']]

def filter_todays_events(events):
    today = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
    return [event for event in events if event['start'].date() <= today <= event['end'].date()]



@app.route('/agenda')
def index():
    #creat a disctionary of events with name and url
    dic_events = {"Sala Multiuso II - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_39uv0cjnnp55namoohfp5reh64%40group.calendar.google.com/public/basic.ics",
               "Sala Multiuso I - 1D": "https://calendar.google.com/calendar/ical/unicamp.br_db9jhcseff6a3shfhn9bpq8oa0%40group.calendar.google.com/public/basic.ics",
               "Sala Laboratório II - 1E": "https://calendar.google.com/calendar/ical/unicamp.br_un4jejd9b9u809p5lckfvknfp8%40group.calendar.google.com/public/basic.ics",
               "Sala Laboratório I - 1D": "https://calendar.google.com/calendar/ical/unicamp.br_prc9hoe8r6kvidn15prn7napao%40group.calendar.google.com/public/basic.ics",
               "Sala de Idiomas I - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_rg8c8vr5ajf1p2rvd9hnihkg2g%40group.calendar.google.com/public/basic.ics",
               "Sala Auditório - 1E": "https://calendar.google.com/calendar/ical/unicamp.br_o4lfdobcojlmdcrgcp2kvpkm7c%40group.calendar.google.com/public/basic.ics"
    }
    #dic_events = {"Sala de Idiomas I - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_rg8c8vr5ajf1p2rvd9hnihkg2g%40group.calendar.google.com/public/basic.ics"
    #              }

    all_events = []
    for location, ics_url in dic_events.items():
        ics_content = fetch_ics(ics_url)
        events = parse_ics(ics_content)
        for event in events:
            event['location'] = location
            all_events.append(event)

    # Filter events
    current_events = filter_current_events(all_events)
    todays_events = filter_todays_events(all_events)

    # Group events by location and sort by start time (optional)
    todays_events.sort(key=lambda x: (x['location'], x['start']))
    events_by_location = {k: list(g) for k, g in groupby(todays_events, key=lambda x: x['location'])}

    current_date = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y")
    return render_template('index.html', current_events=current_events, events_by_location=events_by_location, current_date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
