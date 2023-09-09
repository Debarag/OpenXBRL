"""
Sample script to test and run downloaders and parsers.
"""

from openxbrl import Downloader, AccountingParser

test_download = False
test_parse    = True

if( test_download ) :
  downloader = Downloader( './sec-data/forms' )
  ciks = [1750] # AAR Corp # [1341439, 34088]  # Oracle Corp, ExxonMobil
  forms = ["10-K", "10-K/A", "10-Q", "10-Q/A"]
  downloader.get(ciks, forms, '2000-01-01', '2023-06-30')

if( test_parse ) :
    # Assumes companyfacts.zip from SEC has been downloaded and unzipped
    # small test: 
    ciks = [1750, 1341439, 34088, 28412] # AAR copr, Oracle, ExxonMobil, Comerica
    ap   = AccountingParser('./sec-data/companyfacts/')
    # full set:
    # ciks = ap.get_CIK_list()
    ap.parse_files_to_csv( ciks=ciks, outputfile='./sec-data/dataset.csv')

