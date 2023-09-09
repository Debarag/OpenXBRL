"""
Downloader of SEC Edgar data
"""
import os
import requests
import json
import pandas
import time 


class Downloader( ) :

  def __init__( self, working_dir : str ) :
    self._working_dir = working_dir
    os.makedirs( working_dir,exist_ok=True)


  def get( self, ciks, forms, from_date, to_date ) -> None :
    """
    Downloads and saves Edgar data to working dir.
    Parameters:
      ciks  : list of CIK numbers of firms
      forms : list of SEC forms to download
      from_date : start of period to download in 'yyyy-mm-dd' format
      to_date   : end of period to download   in 'yyyy-mm-dd' format
    """

    # Helper function to access Edgar site
    def load_url(url):
      # Wait a bit as per SEC Edgar rate use requirements
      time.sleep(0.11)
    
      response = requests.get(url,headers={"User-Agent": "Mozilla/5.0"})
      if response.status_code != 200:
        raise Exception(f"Failed to fetch data from URL: {url}")
      return response.content

    num_files = 0 

    for cik in ciks :
      cik = int(cik)  
      url = f"https://data.sec.gov/submissions/CIK{cik:010}.json"

      data = json.loads(load_url(url))

      # Convert JSON to dataframe for easier use
      recents = pandas.DataFrame(data['filings']['recent'])
      recents['reportDate'] = pandas.to_datetime(recents['reportDate'])
      recents['filingDate'] = pandas.to_datetime(recents['filingDate'])

      for form in forms :

        df = recents[(recents['form'] == form) &
            (recents['filingDate'] >= from_date) &
            (recents['filingDate'] <= to_date  ) ]

        for i in range(len(df)) :
          row = df.iloc[i]
          accessionNumber = row['accessionNumber'].replace("-", "")
          filename        = f"{row['accessionNumber']}.txt"
          url = f"https://www.sec.gov/Archives/edgar/data/{cik:010}/{accessionNumber}/{filename}"
          content = load_url(url)

          with open(os.path.join(self._working_dir, filename), "wb") as f:
            f.write(content)
          
          num_files += 1
          print(f"Downloaded CIK:{cik} Form:{form} to {filename}")
    print( f"Download request finished. {num_files} files fetched.")
    # end get()
           
# end Downloader()
