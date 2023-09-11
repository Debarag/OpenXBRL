"""
Downloader of SEC Edgar data
"""
import os
import requests
import json
import pandas
import time 


class Downloader( ) :


  def get_urls( self, ciks, forms, from_date, to_date ) -> pandas.DataFrame :
    """
    Returns DataFrame with URLs to Edgar data based on query criteria
    Parameters:
      ciks  : list of CIK numbers of firms
      forms : list of SEC forms 
      from_date : start of period in 'yyyy-mm-dd' format
      to_date   : end of period  in 'yyyy-mm-dd' format
    Returns :
      pandas.DataFrame with columns CIK, filing_date, form, URL
    """
    sec_data = dict()
    
    for cik in ciks :
      cik = int(cik)  
      url = f"https://data.sec.gov/submissions/CIK{cik:010}.json"

      data = json.loads(self._load_url(url))

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

          sec_data[ (cik, form, row['filingDate']) ] = { 'URL': url, 'filename' : filename }

    # Convert dict to DataFrame
    df = pandas.DataFrame.from_dict( sec_data, orient='index' )
    xf = pandas.DataFrame.from_records( df.index, columns=['CIK', 'form', 'filing_date'])
    df.reset_index(inplace=True)
    df = df.join(xf)
    return df[['CIK', 'form', 'filing_date', 'URL', 'filename']]
    # end get_urls()


  def get_files( self, ciks, forms, from_date, to_date, workingdir : str ) -> None :
    """
    Downloads and saves Edgar data to working dir.
    Parameters:
      ciks  : list of CIK numbers of firms
      forms : list of SEC forms to download
      from_date : start of period to download in 'yyyy-mm-dd' format
      to_date   : end of period to download   in 'yyyy-mm-dd' format
      workingdir : folder to download files to
    """
    os.makedirs( workingdir, exist_ok=True)

    num_files = 0 

    df = self.get_urls( ciks, forms, from_date, to_date )
    for ndx in range(0,len(df)) :
      row = df.iloc[ndx]

      filename = row['filename']
      url      = row['URL']
      cik      = row['CIK']
      form     = row['form']
      content = self._load_url(url)

      with open(os.path.join(workingdir, filename), "wb") as f:
        f.write(content)
      
      num_files += 1
      print(f"Downloaded CIK:{cik} Form:{form} to {filename}")
    print( f"Download request finished. {num_files} files fetched.")
  # end get_files()

        
  def _load_url(self, url : str) :
    """
    Helper function to download URLs from EDGAR
    """
    # Wait a bit as per SEC Edgar rate use requirements
    time.sleep(0.11)
  
    response = requests.get(url,headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
      raise Exception(f"Failed to fetch data from URL: {url}")
    return response.content
  # end _load_url()
           
# end Downloader()
