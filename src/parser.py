from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
from tabulate import tabulate

def parse_reports():

    html_data = Path.cwd().joinpath("data/CodeQuality/result/index.html")
    with open(html_data) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    page_title = soup.h1.span.text

    tables = soup.find_all('table', {'class' : 'CoverPageTable'})

    df_tables = []

    for table in tables:
        df_tables.append(pd.read_html(str(table))[0])
    df_tables = pd.concat(df_tables)

    df_tables.columns = ["Overview", "Report Value"]

    print(tabulate(df_tables, tablefmt="pipe", headers="keys"))

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

    result = tabulate(quality_report_details, tablefmt="pipe", headers="keys")
    return result
    
    