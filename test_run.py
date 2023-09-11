"""
Sample script to test and run downloaders and parsers.
"""

from openxbrl import Downloader, AccountingParser

test_download = True
test_parse    = False

if( test_download ) :
  downloader = Downloader(  )
  ciks      = [1750] # AAR Corp # [1341439, 34088]  # Oracle Corp, ExxonMobil
  forms     = ["10-K", "10-K/A", "10-Q", "10-Q/A"]
  from_date = '2022-01-01'
  to_date   = '2023-09-01'
  df = downloader.get_urls(ciks, forms, from_date, to_date)
  print(df)
  downloader.get_files(ciks, forms, from_date, to_date, workingdir='./sec-data/forms')

if( test_parse ) :
    # Assumes companyfacts.zip from SEC has been downloaded and unzipped
    # small test: 
    ciks = [1750, 1341439, 34088, 28412] # AAR Corp, Oracle, ExxonMobil, Comerica
    ap   = AccountingParser('./sec-data/companyfacts/')
    # full set:
    # ciks = ap.get_CIK_list()
    ap.parse_files_to_csv( ciks=ciks, outputfile='./sec-data/dataset.csv')

