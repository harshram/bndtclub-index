import os
import markdown
import json

def description_text_by_quarter(country):
    '''
    Load up the markdown contents into a viable data structure which is able to preserve the
    historical. 
    '''
    highlights_text_by_country = {}
    highlights_text_by_year = {}

    load_md_files(highlights_text_by_country, highlights_text_by_year)

    return highlights_text_by_country[country]

def description_text_by_countries():
    highlights_text_by_country = {}
    highlights_text_by_year = {}

    load_md_files(highlights_text_by_country, highlights_text_by_year)

    return highlights_text_by_year


def load_md_files(highlights_text_by_country, highlights_text_by_year, base_path='docs/contents'):
    '''
    Load Markdown files into and easy-to-parse data structures which maintains the historical
    information. 
    It is a dual construction. By country and by year, depending on how those information need
    to be then parsed.
    '''
    years = os.listdir(f'{base_path}')
    for year in years:
        # Top-level folder may have files, let's skip them
        if os.path.isfile(f'{base_path}/{year}'):
            continue
        highlights_text_by_year[year] = {}
        try:
            # print(f'{year}')
            quarters = os.listdir(f'{base_path}/{year}')
            for quarter in quarters:
                # print(f'  {quarter}')
                highlights_text_by_year[year][quarter] = {}
                files = os.listdir(f'{base_path}/{year}/{quarter}')
                for file in files:
                    # print(f'   {file}')
                    country = file[:2]
                    if country not in highlights_text_by_country:
                        highlights_text_by_country[country] = {}
                    if year not in highlights_text_by_country[country]:
                        highlights_text_by_country[country][year] = {}
                    if quarter not in highlights_text_by_country[country][year]:
                        highlights_text_by_country[country][year][quarter] = {}
                    with open(f'{base_path}/{year}/{quarter}/{file}', 'r') as content:
                        md = content.read()
                        highlights_text_by_country[country][year][quarter] = md
                        highlights_text_by_year[year][quarter][country] = md

        except NotADirectoryError:
            pass

def load_md_overview(file_name='intro.md', base_path='docs/dtpi'):
    '''
    Load from file the Markdown for the overview section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return markdown.markdown(f.read())

    return None

def load_md_introduction(file_name='intro.md', base_path='docs/dtpi'):
    '''
    Load from file the Markdown for the introduction section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return f.read()

    return None


def load_md_methodology(file_name='methodology.md', base_path='docs/dtpi'):
    '''
    Load from file the Markdown for the introduction section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return f.read()

    return None

def load_md_howto(file_name='howto.md', base_path='docs/dtpi'):
    '''
    Load from file the Markdown for the how to section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return f.read()

    return None

def load_md_welcome(file_name='welcome.md', base_path='docs/dtpi'):
    '''
    Load from file the Markdown for the how to section
    '''
    with open(f'{base_path}/{file_name}', 'r') as f:
        return f.read()

    return None
