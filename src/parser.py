from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
from tabulate import tabulate

def parse_reports(options):

    html_data = Path.cwd().joinpath(options["HTML_FILE"])
    with open(html_data) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    page_title = soup.h1.span.text

    tables = soup.find_all('table', {'class' : 'CoverPageTable'})

    df_tables = []

    for table in tables:
        df_tables.append(pd.read_html(str(table))[0])
    df_tables = pd.concat(df_tables)

    df_tables.columns = ["Overview", "Report Value"]
    emoticon_dict = {"passed": ":white_check_mark:", "failed": ":x:", "errors": ":heavy_exclamation_mark:"}
    df_tables["Report Value"] = df_tables["Report Value"].str.lower()
    df_tables["Overview"] = df_tables["Overview"].str.rstrip(":")
    conclusion = df_tables.loc[df_tables["Overview"]=="Overall Result","Report Value"].item()
    df_tables["Report Value"] = df_tables["Report Value"].replace(emoticon_dict)
    summary = tabulate(df_tables[-3:].reset_index(drop=True), tablefmt="pipe", headers="keys")
    summary_dict = df_tables[-3:].to_dict('list')

    file_names = soup.find_all('h4', {'class' : 'Heading4'})
    m_file_names = [file_name.text.split("Analysis=")[-1]+".m" for file_name in file_names if "Analysis" in file_name.text]
        
    file_results = soup.find_all('p', {'class' : 'TestDetails'})
    test_status = []
    test_duration = []
    for file_result in file_results:
        result = file_result.text.split('\n')
        test_status.append(result[0].split('test ')[-1].strip('.'))
        test_duration.append(result[-1].split('Duration: ')[-1])

    quality_report_details = pd.DataFrame({"File Names": m_file_names,
                                        "Test Status": test_status,
                                        "Test Duration": test_duration})
    quality_report_details["Test Status"] = quality_report_details["Test Status"].replace(emoticon_dict)

    result = tabulate(quality_report_details.reset_index(drop=True), tablefmt="pipe", headers="keys")
    return summary, result, conclusion, summary_dict
    
    