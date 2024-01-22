#down load data from the API
def read_data(url: str) -> list[dict]:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            #only get the results
            data = response.json()['results']
            if isinstance(data,list):
                return data
            else:
                print('the data received is not a list of dictionary')
        else:
            print('failed to load data from the API. Status code is {response.status_code}')
    except Exception as e:
        print(' an error occured {e}')
   
#extract downloaded data 
def extract_data(data: list[dict]) -> list[list[str], list[str], list[str], list[str], list[str]]:
    companies = [item['company']['name'] for item in data]
    locations = [item['locations'][0]['name'] for item in data]
    jobs = [item['name'] for item in data]
    job_type = [item['type'] for item in data]
    publication_date = [item['publication_date'] for item in data]
    return companies, locations, jobs, job_type, publication_date

   


if __name__ == '__main__':
    import requests
    import pandas as pd  
    import subprocess
    from typing import List
    import toml
    config_data = toml.load('config.toml')
    url = config_data['config']['url']
    shared_key = config_data['config']['shared_key']
    
       
    data = read_data(url)
    li = extract_data(data)
    # convert the data (list of list) by transposing first, then convert to data frame, and lastly export to filename
    transposed_list = list(map(list,zip(*li)))
    df = pd.DataFrame(transposed_list, columns=['Company','Location','Job','Job_type','Publication_date'])
    df[['City','Country-State']]=df['Location'].str.split(',',expand=True)
    df = df.drop(['Location'],axis=1)
    df.to_csv('demo.csv',index=False)
    #upload file to blob container on azure storage account
    #recursive to allow copy multiple files just in case
    subprocess.run(['azcopy','copy','demo.csv', shared_key,'--recursive=true','--overwrite=true'])
    