import requests
import base64
import os
import xml.etree.ElementTree as ET
import time
#look into scraping CSES or using wix api
class WildApricotAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_access_token(self):
        encoded_api_key = base64.b64encode(f"APIKEY:{self.api_key}".encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = 'grant_type=client_credentials&scope=auto&obtain_refresh_token=true'

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Failed to retrieve token: {response.content}")

    def download_attachment(self, file_id, folder_path):
        try:
            url = f'{self.base_url}/attachments/{file_id}'
            response = requests.get(url, headers=self.get_headers())
            print(f'Trying {file_id}') # Debug
            if response.status_code == 200:
                file_path = os.path.join(folder_path, f'{file_id}.pdf')
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f'File saved as {file_path}') # Debug
        except Exception as e:
            print(e)

def download_all_files():
    if not os.path.exists('files'):
        os.makedirs('files')
    account_id = '322042'
    api_key = os.environ.get('wildapiricot_api_key')
    api = WildApricotAPI(api_key, account_id)
    local_path = os.path.join(os.getcwd(), 'files') #./files
    xml_file_path = os.path.join(os.getcwd(), 'Members.xml') # ./Members.xml

    file_ids = api.extract_file_ids(xml_file_path)

    ratelimitThrottle = True # If file is skipped, do not wait 1 second.
    
    print('Will take a while...')
    for file_id_set in file_ids:
        if ratelimitThrottle == True:
            time.sleep(1) # Theres some kind of rate limit on WildApricot, though they don't disclose it.
        for resume_id in file_id_set['Resume']:
            resume_file = os.path.join(local_path, resume_id.strip() + '.pdf')
            if not os.path.exists(resume_file) or os.path.exists(resume_file.replace('.pdf', '.doc')): 
                api.download_attachment(resume_id.strip(), local_path)
                ratelimitThrottle=True
            else:
                ratelimitThrottle=False # If file doesnt exist in the directory, skip. No need to pause later, as the file id is taken from XML and not WildApricot.
                print(f'Skipped. {resume_file} already exists.')

        for bio_id in file_id_set['Bio']:
            bio_file = os.path.join(local_path, bio_id.strip() + '.pdf')
            if not (os.path.exists(bio_file) or os.path.exists(bio_file.replace('.pdf', '.doc'))):
                api.download_attachment(bio_id.strip(), local_path)
                ratelimitThrottle=True
            else:
                ratelimitThrottle=False
                print(f'Skipped. {bio_file} already exists.')
    print('DONE!')
            
if __name__ == "__main__":
    download_all_files()