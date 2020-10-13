api_request_id = '{"state":"authen","type":"request","value":"id"}'
api_request_close = '{"state":"authen","type":"notification","value":"close"}'
api_request_pass = '{"state":"authen","type":"response","value":"pass"}'

api_response_sensor_done = '{"state":"provide","type":"response","value":"sensor","data":"done"}'
api_response_sensor_fail = '{"state":"provide","type":"response","value":"sensor","data":"fail"}'

def api_response_time(year, month, day, hour, minute, second ):
    json = {
        "state": "provide",
        "type": "response",
        "value": "time",
        "data": {
            "time": [hour, minute, second],
            "date": [day, month, year]
            }
    }
    return json


# def api_response_sensor(json):




