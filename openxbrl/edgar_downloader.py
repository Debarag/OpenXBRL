"""
Downloader of SEC Edgar data
"""
import os
import requests
import json
import pandas
import time 


class Downloader( ) :

  def get_CIKs_from_tickers( self, tickers = None ) -> dict :
    """
    Get CIKs and company names from stock tickers
    Parameters:
      tickers   : optional, list of tickers. Get all tickers if None.
    Returns :
      Dictionary with tickers as keys
    """
    url  = f"https://www.sec.gov/files/company_tickers.json"
    data = json.loads(self._load_url(url))
    out  = dict()
    for d in data:
      ticker      = data[d]['ticker'].upper()
      out[ticker] = {'CIK' : int(data[d]['cik_str']), 'title' : data[d]['title'] }
    
    if( tickers == None ) :
      return out
    else :
      xout = dict()
      for t in tickers:
        x = out.get(t.upper())
        if( x != None ) :
          xout[t.upper()] = x
      return xout


  def get_companyfacts( self, cik : int, workingdir : str ) -> str :
    """
    Downloads a single companyfacts JSON file to the working dir
    Parameters: 
      cik         : CIK id for company
      workingdir  : path to folder to which do download the file
    Returns:
      name of JSON file downloaded
    """
    filename  = f"CIK{cik:010}.json" 
    url       = f"https://data.sec.gov/api/xbrl/companyfacts/{filename}"
    content   = self._load_url(url)

    if( not os.path.exists(workingdir) ) :
      os.makedirs(workingdir, exist_ok=True)

    outfile   = os.path.join(workingdir, filename)
    with open(outfile, "wb") as f:
        f.write(content)
    return filename


  def get_single_filing(self, cik : int, accession_number : str) -> str :
    """
    Access SEC EDGAR to pull down a filing for a particular CIK, by Accession Number
    Parameters:
      cik   : CIK of company
      accession_number : The ID of the filing. This must be found beforehand.
    Returns :
      The raw text of the filing (includes all HTML and XBRL)
    """
    url_list = self.get_filing_URLs( cik, [accession_number] )
    url      = url_list[0]
    if( url == None ) :
      return None
    return self._load_url(url)


  def get_filing_URLs(self, cik : int, accession_numbers : list) -> list :
    """
    Get URLs for SEC EDGAR to pull down filings for a particular CIK, by Accession Number
    Parameters:
      cik   : CIK of company
      accession_numbers : A list of IDs of the filing. This must be found beforehand.
    Returns :
      List of URLs of the primary document for each accession number.
    """
    url  = f"https://data.sec.gov/submissions/CIK{cik:010}.json"
    data = json.loads(self._load_url(url))

    # Convert JSON to dataframe for easier use
    recents = pandas.DataFrame(data['filings']['recent'])

    url_list = list()
    for accession_number in accession_numbers :
      df = recents.loc[recents['accessionNumber']==accession_number]

      if( len(df) == 0 ) :
        print(f"[ERROR] Cannot find filing for this CIK: {cik}, Accession number: {accession_number}")
        url_list.append(None)
      else :
        primaryDocument = df.iloc[0]['primaryDocument']
        acc_num         = accession_number.replace("-", "")

        url = f"https://www.sec.gov/Archives/edgar/data/{cik:010}/{acc_num}/{primaryDocument}"
        url_list.append(url)
    return url_list
  

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
          primaryDocument = row['primaryDocument']
          accessionNumber = row['accessionNumber'].replace("-", "")
          filename        = f"{row['accessionNumber']}.txt"
          url = f"https://www.sec.gov/Archives/edgar/data/{cik:010}/{accessionNumber}/{filename}"

          sec_data[ (cik, form, row['filingDate']) ] = { 'URL': url, 'filename' : filename, 'filing_filename' : primaryDocument }

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
