import datetime
import json
import aprs

def lambda_handler(event, context):
    http = event['requestContext']['http']
    if http['method'] == "POST":
        callsign = http['path'].split("/")[1]
        if not callsign:
            return {
                'statusCode': 400,
                'body': "Please pass a callsign in the path"
            }
        data = json.loads(http['body'])
        print(data)

        lat = data['iridium_latitude']
        lon = data['iridium_longitude']
        timestamp = datetime.datetime.strptime(data['transmit_time'], "%y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        altitude = None
        comment = ""

        with aprs.APRS() as server:
            server.login(callsign)

            report = aprs.position_report(
                callsign=callsign,
                latitude=lat,
                longitude=lon,
                timestamp=timestamp,
                altitude=altitude,
                comment=comment)

            server.send(report)

        return {
            'statusCode': 200,
            'body': json.dumps(report)
        }
    data = {
        "imei": 300234010753370,
        "serial": 12345,
        "momsn": 12345,
        "transmit_time": "21-10-31 10:41:50",
        "iridium_latitude": 10.0,
        "iridium_longitude": 20.0,
        "iridium_cep": 8,
        "data": "48656c6c6f20576f726c6420526f636b424c4f434b"
    }
    return {
        'statusCode': 200,
        'body': "Please submit a json object as a POST request, with the desired callsign in the path.\n" + json.dumps(data, indent=2)
    }
