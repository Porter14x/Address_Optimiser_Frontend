import os.path
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

OPTIMISED_SHEET_ID = os.getenv("OPTIMISED_SHEET_ID")
MASS_INSERT_SHEET_ID = os.getenv("MASS_INSERT_SHEET_ID")
SERVER_URL = os.getenv("SERVER_URL")
OPT_PV_ID = os.getenv("OPT_PV_ID")
OPT_OP_ID = os.getenv("OPT_OP_ID")
IN_PV_ID = os.getenv("IN_PV_ID")
START_ADDRESS = os.getenv("START_ADDRESS")
END_ADDRESS = os.getenv("END_ADDRESS")

#address values on spreadsheet start at 4th row (ie A4)
ADD_START = 4

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds

def optimiseJobSheet():
    creds = authenticate()
    adds_and_notes = []
    adds_post = []

    try:
        service = build("sheets", "v4", credentials=creds)

        range_names = [
            "Plain_Values!A4:A",
            "Plain_Values!B4:B",
            "Plain_Values!C4:C",
        ]

        result = (
            service.spreadsheets()
            .values()
            .batchGet(spreadsheetId=OPTIMISED_SHEET_ID, ranges=range_names)
            .execute()
        )

        adds = result["valueRanges"][0]["values"]
        mid = result["valueRanges"][1]["values"]
        notes = result["valueRanges"][2]["values"]

        #sheets will omit leading empty cells, so making sure empty notes are still present
        longest_arr = max(len(adds), len(mid), len(notes))
        while(len(adds)<longest_arr or len(mid)<longest_arr or len(notes)<longest_arr):
            if len(adds)<longest_arr:
                adds.append([])
            if len(mid)<longest_arr:
                mid.append([])
            if len(notes)<longest_arr:
                notes.append([])

        #empty adds vals are made by the postcode headers, getting rid of them to not confuse Nominatim
        ix = 0
        while ix < len(adds):
            if adds[ix] == []:
                adds.pop(ix)
                mid.pop(ix)
                notes.pop(ix)
                #restart loop
                ix = 0
            else:
                ix += 1

        for i in range(len(adds)):
            #since some of these vals will be [], mid[i][0] or notes[i][0] could throw an IndexError
            mid_input = ""
            notes_input = ""

            if mid[i] == []:
                mid_input = ""
            else:
                mid_input = mid[i][0]
            
            if notes[i] == []:
                notes_input = ""
            else:
                notes_input = notes[i][0]

            adds_and_notes.append({"address": adds[i][0], "mid": mid_input, "notes": notes_input})
            adds_post.append({"q": adds[i][0].replace("\n", " ").strip(), "format": "json"})

        adds_and_notes.insert(0, {"address": START_ADDRESS, "mid": "", "notes": ""})
        adds_and_notes.insert(-1, {"address": END_ADDRESS, "mid": "", "notes": ""})

        adds_post.insert(0, {"q": START_ADDRESS.replace("\n", " ").strip(), "format": "json"})
        adds_post.insert(-1, {"q": END_ADDRESS.replace("\n", " ").strip(), "format": "json"})

        response_adds = requests.post(f"{SERVER_URL}/optimise", json={"addresses": adds_post}).json()
        print(f"len(response_adds): {len(response_adds)}")
        print(f"len(adds_and_notes): {len(adds_and_notes)}")

        opt_adds = []
        for add in response_adds:
            if adds_and_notes[add["original_index"]]["address"] == START_ADDRESS:
                continue
            elif adds_and_notes[add["original_index"]]["address"] == END_ADDRESS:
                continue
            opt_adds.append(adds_and_notes[add["original_index"]])
        
        writeAddsToJobSheet(opt_adds, service)
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def writeAddsToJobSheet(opt_adds, service):
    try:
        service.spreadsheets().values().clear(
        spreadsheetId=OPTIMISED_SHEET_ID,
        range=f"Optimised!{ADD_START}:1000"
        ).execute()

        A_values = []
        B_values = []
        C_values = []
        for val in opt_adds:
            A_values.append([val["address"]])
            B_values.append([val["mid"]])
            print(f"val[mid]: {val["mid"]}")
            C_values.append([val["notes"]])
            print(f"val[notes]: {val["notes"]}")
        
        data = [
            {"range": f"Optimised!A{ADD_START}:A{ADD_START+len(opt_adds)-1}", "values": A_values},
            {"range": f"Optimised!B{ADD_START}:B{ADD_START+len(opt_adds)-1}", "values": B_values},
            {"range": f"Optimised!C{ADD_START}:C{ADD_START+len(opt_adds)-1}", "values": C_values},
        ]
        
        body = {"valueInputOption": "USER_ENTERED", "data": data}

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=OPTIMISED_SHEET_ID, body=body).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

if __name__ == "__main__":
    optimiseJobSheet()