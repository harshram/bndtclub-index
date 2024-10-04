
def description_text(country):

    available_text = {
        "DE" : """
                This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.
                - **X-axis**: Represents the normalized employment growth in the IT sector.
                - **Y-axis**: Represents the normalized labor growth in the IT sector.
                - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
                - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
                - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.
                Hover over the bubbles to see details about the specific quarter and country data.
                """
            ,
        "IT" : """
                How the DTPI Reflects the Evolution of Inputs

                - Early Period (2020-Q4 to 2021-Q2):  
                The sharp drop in the index mirrors the significant decline in GVA, despite relatively stable ICT Employment and moderate Labour Demand. The index reflects inefficiency in the ICT sector during this time, where economic output declines faster than employment growth, signaling underperformance.

                - Stagnation Phase (2021-Q2 to 2022-Q1):  
                During this period, the index remains low as GVA stays depressed, Labour Demand decreases, and ICT Employment grows only slightly. The index captures this stagnation by reflecting a lack of significant improvements in economic output or future job creation, showing minimal potential for growth.

                - Recovery and Growth (2022-Q2 to 2023-Q1):  
                As GVA increases and ICT Employment expands, the index rises sharply. This indicates improved efficiency in the ICT sector. The stabilization and rise in Labour Demand further boosts the index, signaling positive future expectations.

                - Recent Volatility (2023-Q2 to 2024-Q1):  
                The index becomes more volatile, reflecting fluctuations in GVA and Labour Demand, while ICT Employment remains relatively stable. The instability in the index mirrors the uncertain future prospects for the ICT sector, with both potential growth and risks present.
                """
            ,
        "FR" : """
                This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.

                - **X-axis**: Represents the normalized employment growth in the IT sector.
                - **Y-axis**: Represents the normalized labor growth in the IT sector.
                - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
                - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
                - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.

                Hover over the bubbles to see details about the specific quarter and country data.
                """
            ,
        "ES" : """
            This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.

            - **X-axis**: Represents the normalized employment growth in the IT sector.
            - **Y-axis**: Represents the normalized labor growth in the IT sector.
            - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
            - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
            - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.

            Hover over the bubbles to see details about the specific quarter and country data.
            """
        ,
        "NL" : """
            This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.

            - **X-axis**: Represents the normalized employment growth in the IT sector.
            - **Y-axis**: Represents the normalized labor growth in the IT sector.
            - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
            - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
            - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.

            Hover over the bubbles to see details about the specific quarter and country data.
        """
     }
    
    return available_text[f"{country}"]

def description_text_by_quarter(country):
    '''
    Load up the markdown contents into a viable data structure which is able to preserve the
    historical. 
    '''
    highlights_text = {}
    load_md_files(highlights_text)

    return highlights_text[country]

import os
import markdown

def load_md_files(highlights_text, base_path='docs'):
    '''
    Load Markdown files into and easy-to-parse data structure which maintains the historical
    '''
    years = os.listdir(f'{base_path}')
    for year in years:
        try:
            # print(f'{year}')
            quarters = os.listdir(f'{base_path}/{year}')
            for quarter in quarters:
                # print(f'  {quarter}')
                files = os.listdir(f'{base_path}/{year}/{quarter}')
                for file in files:
                    # print(f'   {file}')
                    if file[:2] not in highlights_text:
                        highlights_text[file[:2]] = {}
                    if year not in highlights_text[file[:2]]:
                        highlights_text[file[:2]][year] = {}
                    if quarter not in highlights_text[file[:2]][year]:
                        highlights_text[file[:2]][year][quarter] = {}
                    with open(f'{base_path}/{year}/{quarter}/{file}', 'r') as content:
                        highlights_text[file[:2]][year][quarter] = markdown.markdown(content.read())
        except NotADirectoryError:
            pass

def load_md_overview(file_name='DTPI.md', base_path='docs'):
    '''
    Load from file the Markdown for the overview section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return markdown.markdown(f.read())

    return None