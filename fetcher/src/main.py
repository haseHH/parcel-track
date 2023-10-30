from fastapi import FastAPI
from pydantic import BaseModel
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

#region Models
class Status(BaseModel):
    id: int
    code: str
    name: str
    description: str
    hasBeenReached: bool
    isCurrentStatus: bool
    date: str | None = None

class StatusInfo(BaseModel):
    statesCount: int
    currentState: int | None = None
    states: list[Status]

class TrackingInfo(BaseModel):
    parcelno: str
    zip: str | None = None
    details_link: str
    status: StatusInfo
    orig: dict | None = None
#endregion Models

@app.get(
    "/dpd", tags=["carriers"],
    summary="DPD Germany",
    response_model=TrackingInfo,
    response_description="Tracking info",
)
def dpd(parcelno: str, zip: str | None = None, locale: str = "en_US", includeOriginalApiResponse: bool = False):
    """
    Fetch the tracking info of a package carried by DPD Germany.

    - **parcelno**: The number of your parcel.
    - **zip**: The ZIP code of the recipient. Won't grant any more detail in the tracking status, but setting it will include it in the `weblink`, saving you a step when opening the official tracking page.
    - **locale**: Specifies the language of the status labels and descriptions, default is `en_US`, other known options include: `de_DE`, `fr_FR`
    - **includeOriginalApiResponse**: If `true`, the response will include the original JSON response from the DPD API in `orig`, useful for debugging or adding your own client logic.
    """

    r = requests.get(f"https://tracking.dpd.de/rest/plc/{locale}/{parcelno}")

    if (zip == None):
        weblink = f"https://my.dpd.de/redirect.aspx?parcelno={parcelno}&action=2"
    else:
        weblink = f"https://my.dpd.de/redirect.aspx?zip={zip}&parcelno={parcelno}&action=2"

    statesCount: int = len(r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"])

    response: TrackingInfo = {
        "parcelno": parcelno,
        "zip": zip,
        "details_link": weblink,
        "status": {
            "statesCount": statesCount,
            "currentState": None,
            "states": [],
        },
    }

    for i in range(statesCount):
        state: Status = {
            "id": i,
            "code": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i]["status"],
            "name": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i]["label"],
            "description": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i]["description"]["content"][0],
            "hasBeenReached": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i]["statusHasBeenReached"],
            "isCurrentStatus": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i]["isCurrentStatus"],
            "date": r.json()["parcellifecycleResponse"]["parcelLifeCycleData"]["statusInfo"][i].get("date"),
        }
        response["status"]["states"].append(state)

        if state["isCurrentStatus"]:
            response["status"]["currentState"] = i

    if (includeOriginalApiResponse):
        response["orig"] = r.json()

    return response
