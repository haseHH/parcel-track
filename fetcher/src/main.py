from fastapi import FastAPI
from typing import Union
import requests

app = FastAPI(
    title="parcel-track-fetcher",
    description="This `fetcher` serves as a sort of wrapper for tracking parcels through various services.",
    contact={
        "name": "See the source code on GitHub",
        "url": "https://github.com/haseHH/parcel-track",
    },
    license_info={
        "name": "License",
        "url": "https://github.com/haseHH/parcel-track/blob/main/LICENSE",
    },
    docs_url="/",
    redoc_url=None,
)

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
