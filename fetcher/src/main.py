from fastapi import FastAPI
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
    openapi_tags=[
        {
            "name": "carriers",
            "description": "These functions represent the supported carriers.",
        },
    ],
)

@app.get("/dpd", tags=["carriers"], summary="DPD Germany")
def dpd(parcelno: str, zip: str | None = None, locale: str = "en_US"):
    """
    Fetch the tracking info of a package carried by DPD Germany.

    - **parcelno**: The number of your parcel.
    - **zip**: The ZIP code of the recipient. Won't grant any more detail in the tracking status, but setting it will include it in the `weblink`, saving you a step when opening the official tracking page.
    - **locale**: Specifies the language of the status labels and descriptions, default is `en_US`, other known options include: `de_DE`, `fr_FR`
    """

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
