from fastapi import FastAPI
from typing import Union
import requests

app = FastAPI()

@app.get("/")
def index():
    return {"hello": "world"}

@app.get("/dpd")
def dpd(parcelno: str, zip: Union[str, None] = None, locale: str = "en_US"):
    r = requests.get(f"https://tracking.dpd.de/rest/plc/{locale}/{parcelno}")

    if (zip == None):
        weblink = f"https://my.dpd.de/redirect.aspx?parcelno={parcelno}&action=2"
    else:
        weblink = f"https://my.dpd.de/redirect.aspx?zip={zip}&parcelno={parcelno}&action=2"

    return {
        'parcelno': parcelno,
        'zip': zip,
        'details_link': weblink,
        'orig': r.json()['parcellifecycleResponse']['parcelLifeCycleData']
    }
