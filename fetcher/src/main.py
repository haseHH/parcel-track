from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

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
    code: str | None = None
    name: str | None = None
    description: str | None = None
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
    "/dhl", tags=["carriers"],
    summary="DHL Germany",
    response_model=TrackingInfo,
    response_description="Tracking info",
)
def dhl(parcelno: str, zip: str | None = None, locale: str = "en", includeOriginalApiResponse: bool = False):
    """
    Fetch the tracking info of a package carried by DHL Germany.

    - **parcelno**: The number of your parcel.
    - **zip**: The ZIP code of the recipient. Won't grant any more detail in the tracking status, but setting it will include it in the response.
    - **locale**: Specifies the language of the status labels and descriptions, default is `en`, other known options include: `de`
    - **includeOriginalApiResponse**: If `true`, the response will include the original JSON response from the DHL API in `orig`, useful for debugging or adding your own client logic.
    """

    r = requests.get(
        url=f"https://www.dhl.de/int-verfolgen/?lang={locale}&piececode={parcelno}",
        headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        },
    )

    for l in r.text.splitlines():
        if "JSON.parse(" in l:
            jsonLineRaw = l.strip()
            break
    jsonLine = jsonLineRaw.split("JSON.parse(\"", 1)[1].rstrip("\"),").replace("\\\"", "\"")
    jsonStatusInfo = json.loads(jsonLine)

    statesCount: int = jsonStatusInfo["sendungen"][0]["sendungsdetails"]["sendungsverlauf"]["maximalFortschritt"] + 1

    response: TrackingInfo = {
        "parcelno": parcelno,
        "zip": zip,
        "details_link": f"https://www.dhl.de/{locale}/privatkunden/dhl-sendungsverfolgung.html?piececode={parcelno}",
        "status": {
            "statesCount": statesCount,
            "currentState": jsonStatusInfo["sendungen"][0]["sendungsdetails"]["sendungsverlauf"]["fortschritt"],
            "states": [],
        },
    }

    for i in range(statesCount):
        state: Status = {
            "id": i,
            "description": jsonStatusInfo["sendungen"][0]["sendungsdetails"]["sendungsverlauf"]["events"][i]["status"],
            "hasBeenReached": i <= response["status"]["currentState"],
            "isCurrentStatus": i == response["status"]["currentState"],
            "date": jsonStatusInfo["sendungen"][0]["sendungsdetails"]["sendungsverlauf"]["events"][i].get("datum"),
        }
        response["status"]["states"].append(state)

    if (includeOriginalApiResponse):
        response["orig"] = jsonStatusInfo

    return response

@app.get(
    "/hermes", tags=["carriers"],
    summary="Hermes Germany",
    response_model=TrackingInfo,
    response_description="Tracking info",
)
def hermes(parcelno: str, zip: str | None = None, locale: str = "en", includeOriginalApiResponse: bool = False):
    """
    Fetch the tracking info of a package carried by Hermes Germany.

    - **parcelno**: The number of your parcel.
    - **zip**: The ZIP code of the recipient. Won't grant any more detail in the tracking status, but setting it will fetch receiver details and some more values in the `orig` section of the response.
    - **locale**: Specifies the language of the status labels and descriptions, default is `en`, other known options include: `de`
    - **includeOriginalApiResponse**: If `true`, the response will include the original JSON response from the Hermes API in `orig`, useful for debugging or adding your own client logic.
    """

    r = requests.get(
        url=f"https://api.my-deliveries.de/tnt/parcelservice/parceldetails/{parcelno}",
        headers={
            "authority": "api.my-deliveries.de",
            "accept": "*/*",
            "cache-control": "no-cache, no-store, must-revalidate",
            "origin": "https://www.myhermes.de",
            "referer": "https://www.myhermes.de/",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "x-language": f"{locale}",
        },
    )
    orig = r.json()

    if (zip != None):
        addr = requests.get(
            url=f"https://api.my-deliveries.de/tnt/parcelservice/addressdetails/{parcelno}",
            headers={
                "authority": "api.my-deliveries.de",
                "accept": "*/*",
                "cache-control": "no-cache, no-store, must-revalidate",
                "origin": "https://www.myhermes.de",
                "referer": "https://www.myhermes.de/",
                "sec-ch-ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "x-language": locale,
                "x-zipcode": zip,
            },
        )
        orig["address"] = addr.json()

    response: TrackingInfo = {
        "parcelno": parcelno,
        "zip": zip,
        "details_link": f"https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation#{parcelno}",
        "status": {
            "statesCount": len(orig["parcelHistory"]),
            "currentState": None,
            "states": [],
        },
    }

    for origState in orig["parcelHistory"]:
        if origState.get("statusHistoryShortText"):
            statusName = origState["statusHistoryShortText"]
        else:
            statusName = origState["nextStatusHistoryShortText"]
        state: Status = {
            "id": origState["statusIndex"],
            "code": origState["status"],
            "name": statusName,
            "description": origState.get("statusHistoryText"),
            "hasBeenReached": not origState["nextStatus"],
            "isCurrentStatus": origState["status"] == orig["status"]["parcelStatus"],
            "date": origState.get("timestamp"),
        }
        response["status"]["states"].append(state)

        if state["isCurrentStatus"]:
            response["status"]["currentState"] = state["id"]

    if (includeOriginalApiResponse):
        response["orig"] = orig

    return response

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
    - **zip**: The ZIP code of the recipient. Won't grant any more detail in the tracking status, but setting it will include it in the `details_link`, saving you a step when opening the official tracking page.
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
