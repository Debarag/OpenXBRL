"""
Transforms HTML into plaintext or PDF
"""
from xhtml2pdf import pisa   

def convert_filing_to_pdf( content : str, outputfile : str ) -> None :
    """
    Save filing into PDF format
    Parameters:
        content     : html text of the filing
        outputfile  : PDF file to create
    """
    source_html = content
    result_file = open(outputfile, "w+b")

    pisa.showLogging()
    
    try :
        pisa_status = pisa.CreatePDF(
                source_html,                # the HTML to convert
                dest=result_file)           # file handle to recieve result
        # returns False on success and True on errors
        if( pisa_status.err ) :
            print( '[ERROR] PDF conversion failed.')
    except Exception as e :
        print( '[ERROR] Problem with PDF conversion:')
        print(e)
    finally :
        result_file.close() 



