import pdf_santa_fe_parser
import adhoc_pdf_santa_fe_parser

def parse_pdf(in_pdf_filepath, out_csv_filepath):
    """ Read, parse and process PDF report and produce a CSV """
    try:
        adhoc_pdf_santa_fe_parser.parse_pdf(in_pdf_filepath, out_csv_filepath)
    except:
        pdf_santa_fe_parser.parse_pdf(in_pdf_filepath, out_csv_filepath)
