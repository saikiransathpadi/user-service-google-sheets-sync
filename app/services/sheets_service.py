from googleapiclient.discovery import build
from app.auth import get_user_credentials
from fastapi import HTTPException
from datetime import datetime


class GoogleSheetsService:
    @staticmethod
    async def create_sheet(user_email: str, sheet_name: str):
        try:
            credentials = await get_user_credentials(user_email)

            service = build('sheets', 'v4', credentials=credentials)

            spreadsheet = {
                'properties': {
                    'title': sheet_name
                },
                'sheets': [{
                    'properties': {
                        'title': 'Users',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }]
            }

            result = service.spreadsheets().create(body=spreadsheet).execute()

            sheet_id = result['spreadsheetId']
            sheet_tab_id = result['sheets'][0]['properties']['sheetId']

            headers = [['ID', 'Name', 'Email', 'Role', 'Created At']]
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Users!A1:E1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()

            formatting_request = {
                'requests': [
                    {
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet_tab_id,
                                'startRowIndex': 0,
                                'endRowIndex': 1
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': 0.2,
                                        'green': 0.2,
                                        'blue': 0.2
                                    },
                                    'textFormat': {
                                        'foregroundColor': {
                                            'red': 1.0,
                                            'green': 1.0,
                                            'blue': 1.0
                                        },
                                        'bold': True
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                        }
                    }
                ]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=formatting_request
            ).execute()

            return {
                'sheet_id': sheet_id,
                'sheet_name': sheet_name,
                'sheet_url': f'https://docs.google.com/spreadsheets/d/{sheet_id}'
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create Google Sheet: {str(e)}")

    @staticmethod
    async def sync_to_cloud(user_email: str, sheet_id: str, users_data: list):
        try:
            credentials = await get_user_credentials(user_email)

            service = build('sheets', 'v4', credentials=credentials)

            values = [['ID', 'Name', 'Email', 'Role', 'Created At']]

            for user in users_data:
                created_at_str = user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user['created_at'], datetime) else str(user['created_at'])
                values.append([
                    str(user['_id']),
                    user['name'],
                    user['email'],
                    user['role'],
                    created_at_str
                ])

            service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range='Users!A2:E'
            ).execute()

            if len(values) > 1:
                service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range='Users!A1',
                    valueInputOption='RAW',
                    body={'values': values}
                ).execute()
            else:
                header_values = [values[0]]
                service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range='Users!A1',
                    valueInputOption='RAW',
                    body={'values': header_values}
                ).execute()

            return {
                'message': f'Successfully synced {len(values) - 1} users to Google Sheets',
                'synced_count': len(values) - 1
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to sync to Google Sheets: {str(e)}")

    @staticmethod
    async def sync_from_cloud(user_email: str, sheet_id: str):
        try:
            credentials = await get_user_credentials(user_email)

            service = build('sheets', 'v4', credentials=credentials)

            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='Users!A2:E'
            ).execute()

            rows = result.get('values', [])

            users = []
            for row in rows:
                if len(row) >= 4:
                    user = {
                        'id': row[0] if len(row) > 0 else None,
                        'name': row[1] if len(row) > 1 else '',
                        'email': row[2] if len(row) > 2 else '',
                        'role': row[3] if len(row) > 3 else '',
                        'created_at': row[4] if len(row) > 4 else None
                    }
                    users.append(user)

            return users

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to sync from Google Sheets: {str(e)}")
