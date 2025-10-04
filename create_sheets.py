import google.auth
import pathlib

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError 
from google.oauth2.credentials import Credentials
from pathlib import Path
from dotenv import set_key
from sheets import authenticate

env_file_path = Path(".env")
env_file_path.touch(mode=0o600) #check env exists before creating

sheet_id = ""
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def create_job_sheet(title):
  """
  Creates the Sheet the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
    global sheet_id
    sheet_id = spreadsheet.get("spreadsheetId")
    set_key(dotenv_path=env_file_path, key_to_set="OPTIMISED_SHEET_ID", value_to_set=sheet_id)
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def setJobSheet():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        service = build("sheets", "v4", credentials=creds)

        create_sheet = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': 'Plain_Values'
                        }
                    }
                },
                {
                    'addSheet': {
                        'properties': {
                            'title': 'Optimised'
                        }
                    }
                },
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=create_sheet
        ).execute()

        meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        pv_id = ""
        op_id = ""
        for s in meta["sheets"]:
            if s["properties"]["title"] == "Plain_Values":
                pv_id = s["properties"]["sheetId"]
                set_key(dotenv_path=env_file_path, key_to_set="OPT_PV_ID", value_to_set=str(pv_id))
                continue
            elif s["properties"]["title"] == "Optimised":
                op_id = s["properties"]["sheetId"]
                set_key(dotenv_path=env_file_path, key_to_set="OPT_OP_ID", value_to_set=str(op_id))
                continue
            #break case for when we have necessary ids if there are more sheets in future
            elif pv_id and op_id: 
                break

        format_sheet = {
            'requests': [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 255},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 1,
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 220},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 2,
                            "endIndex": 3,
                        },
                        "properties": {"pixelSize": 260},
                        "fields": "pixelSize",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": pv_id,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {
                            "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                        },
                        "fields": "userEnteredFormat.wrapStrategy",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": op_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 255},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": op_id,
                            "dimension": "COLUMNS",
                            "startIndex": 1,
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 220},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": op_id,
                            "dimension": "COLUMNS",
                            "startIndex": 2,
                            "endIndex": 3,
                        },
                        "properties": {"pixelSize": 260},
                        "fields": "pixelSize",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": op_id,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {
                            "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                        },
                        "fields": "userEnteredFormat.wrapStrategy",
                    }
                },
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=format_sheet
        ).execute()

        values_body = {
           "valueInputOption": "USER_ENTERED",
           "data": [
              {
                "range": "Plain_Values!A1",
                "values": [["=Sheet1!A1"]]
              },
              {
                "range": "Plain_Values!A2",
                "values": [["=ARRAYFORMULA('Sheet1'!B2:B)"]]
              },
              {
                "range": "Plain_Values!B2",
                "values": [["=ARRAYFORMULA('Sheet1'!C2:C)"]]
              },
              {
                "range": "Plain_Values!C2",
                "values": [["=ARRAYFORMULA('Sheet1'!D2:D)"]]
              },
              {
                "range": "Optimised!A1",
                "values": [["=Sheet1!A1"]]
              },
              {
                "range": "Optimised!A2",
                "values": [["=Sheet1!B2"]]
              },
              {
                "range": "Optimised!C2",
                "values": [["=Sheet1!D2"]]
              },
           ]
        }

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, 
            body=values_body
        ).execute()
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

"""def setSheetInsert():

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        service = build("sheets", "v4", credentials=creds)

        create_sheet = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': 'Plain_Values'
                        }
                    }
                },
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=create_sheet
        ).execute()

        meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        pv_id = None
        for s in meta["sheets"]:
            if s["properties"]["title"] == "Plain_Values":
                pv_id = s["properties"]["sheetId"]
                set_key(dotenv_path=env_file_path, key_to_set="IN_PV_ID", value_to_set=pv_id)
                break

        format_sheet = {
            'requests': [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 255},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 1,
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 220},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": pv_id,
                            "dimension": "COLUMNS",
                            "startIndex": 2,
                            "endIndex": 3,
                        },
                        "properties": {"pixelSize": 260},
                        "fields": "pixelSize",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": pv_id,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {
                            "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                        },
                        "fields": "userEnteredFormat.wrapStrategy",
                    }
                },
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=format_sheet
        ).execute()

        values_body = {
           "valueInputOption": "USER_ENTERED",
           "data": [
              {
                "range": "Plain_Values!A1",
                "values": [["=Sheet1!A1"]]
              },
              {
                "range": "Plain_Values!A2",
                "values": [["=ARRAYFORMULA('Sheet1'!B2:B)"]]
              },
              {
                "range": "Plain_Values!B2",
                "values": [["=ARRAYFORMULA('Sheet1'!C2:C)"]]
              },
              {
                "range": "Plain_Values!C2",
                "values": [["=ARRAYFORMULA('Sheet1'!D2:D)"]]
              },
           ]
        }

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, 
            body=values_body
        ).execute()
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
"""
        
def main():
    authenticate()
    create_job_sheet("Address Optimiser MASTER RUN SHEET")
    setJobSheet()
    #create("Address Optimiser Sheet Insert")
    #setSheetInsert()
    
if __name__ == "__main__":
    main()