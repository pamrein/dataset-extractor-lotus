import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep



def get_filename(record_id:str, ACCESS_TOKEN=None):
    """
    Args:
        ACCESS_TOKEN : str
            The access token for the Zenodo API. You have to sign in and make one yourself.
        record_id : str
            The record id of the dataset on Zenodo. It is the the number after records/ in the url.

    Returns:
        filenames : list
            The filenames of the files in the dataset.
    """

    if ACCESS_TOKEN:
        r = requests.get(f"https://zenodo.org/api/records/{record_id}", params={'access_token': ACCESS_TOKEN})
    else:
        r = requests.get(f"https://zenodo.org/api/records/{record_id}")


    download_urls = [f['links']['self'] for f in r.json()['files']]
    filenames = [f['key'] for f in r.json()['files']]

    # add suffix with record_id
    filenames_with_record = [f'{sub} (record: {record_id})' for sub in filenames]

    # print(r.status_code)

    return filenames_with_record, filenames, download_urls


def get_filenames(record_ids:[list, set], ACCESS_TOKEN=None):
    """
    _summary_

    Returns:
        _type_: _description_
    """

    if not ACCESS_TOKEN:
        ACCESS_TOKEN = None

    filenames_list = []
    filenames_record_list = []
    download_urls_list = []

    for record in record_ids:
        filenames_with_record, filenames, download_url = get_filename(ACCESS_TOKEN=ACCESS_TOKEN, record_id=record)
        for file_record in filenames_with_record:
            filenames_record_list.append(file_record)
        for file in filenames:
            filenames_list.append(file)
        for url in download_url:
            download_urls_list.append(url)

    return filenames_record_list, filenames_list, download_urls_list


def download_file(filename, download_url, ACCESS_TOKEN=None):
    """
    Args:
        ACCESS_TOKEN : str
            The access token for the Zenodo API. You have to sign in and make one yourself.
        filename : str
            The filenames of the files in the dataset.
        download_url : str
            The download urls of the files in the dataset.

    Returns:
        path : str
            If file could be downloaded, return path to file. Else, return None.
    """
    # print("Downloading:", filename)
    if ACCESS_TOKEN:
        r = requests.get(download_url, params={'access_token': ACCESS_TOKEN})
    else:
        r = requests.get(download_url)

    with open(filename, 'wb') as f:
            f.write(r.content)

    # print(f"Download complete: {filename}")
    return filename


def get_all_records(url, wait_time=5, headless=True):
    """
    Searchs for all possible DOIs in the given Zenodo website.

        Args:
            url : str
                The url of the Zenodo website with all the versions (for example: 
                https://zenodo.org/search?q=parent.id%3A5794106&f=allversions%3Atrue&l=list&p=1&s=20&sort=version).
            wait_time : int 
                The time in seconds to wait for the website to load.
            headless : bool
                If True, the chrombrowser will be set to headless (browserwindow is hidden). If False, the browserwindow will be visible.

        Returns:
            doi : set
                A set of all the DOIs found with "record" in the linkname.
    """
    
    # Because the website "zenodo" uses javascript for loading the page, we need to use selenium to get the html.
    
    # The chrombrowserfunction can be set to headless (browserwindow is hidden) or not headless.
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')

    # Chrombrowser will be set up 
    driver = webdriver.Chrome(options=chrome_options)

    # Open the webpage and wait <seconds> seconds for the page to load.
    driver.get(url)
    sleep(wait_time) 
    
    # save the html of the webpage
    html = driver.page_source

    # close the Chrombrowser
    driver.quit() 

    # parse the html with BeautifulSoup. lxml: fastest "reader". It helps to encode the html.
    soup = BeautifulSoup(html, 'lxml')

    ## search for links with "record" in the name
    # save the DOIs in a set <dois>
    records = set()

    # search for all possible links in the html
    for a in soup.find_all('a', href=True):
   
        # if the link contains "records", save the link in the set
        if "records" in a['href']:
            record = a['href']

            # remove the record part. Only the DOI will be kept.
            record = record.split('/')[2]

            # add the DOI to the return variable <dois>
            records.add(record)

    return records


def doi_info(doi, print_info=True):
    """
    Gives back the path to downlaod the dataset. It also can display the information of the dataset.
    
        Args:
            doi : str
                The DOI of the dataset.
            print_info : bool
                If True, the filename, version and downloadlink.

        Returns:
            download_link : str
                The link to download the full dataset.
    """

    # good links to download (both files) https://zenodo.org/api/records/5794107/files-archive

    # get the webpagelink from one DOI
    url_doi = 'https://zenodo.org/api/records/' + doi + '/files'

    # get the info as a json file (no API key needed)
    info = requests.get(url_doi)

    info_json = info.json()

    links_for_download = []
    for index in range(len(info_json['entries'])):

        # save information
        filename = info_json['entries'][index]['key']
        info_link = info_json['entries'][index]['links']['self']
        version = info_json['entries'][index]['version_id']
        updated = info_json['entries'][index]['updated']

        # print information
        if print_info:
            print(filename, info_link, version, updated, sep="\n")

        # generate downloadlink (without API key) and add it to the list
        downloadlink = "https://zenodo.org/records/" + doi + "/files/" + filename    
        links_for_download.append(downloadlink)
    
    return links_for_download


def download_file_with_url(url, filename):
    """
    Download the file from the given url and save it as the given filename (optional).

    Args:
        url : str
            The url of the file to download.
        filename : str
            The path with filename with to save. If None, the filename will be the last part of the url and saved in the directory where it was run.

    Returns:

    """
    # get the file from the url
    file_link = requests.get(url, allow_redirects=True)

    # save the file
    if filename:
        open(filename, 'wb').write(file_link.content)
    else:
        # if no filename is given, the filename will be the last part of the url
        filename = url.split('/')[-1]
        open(filename, 'wb').write(file_link.content)
    return



if __name__ == '__main__':
    # zenodo_website_all_versions = "https://zenodo.org/search?q=parent.id%3A5794106&f=allversions%3Atrue&l=list&p=1&s=20&sort=version"
    # lotus_versions = get_all_doi(zenodo_website_all_versions)

    # for doi in lotus_versions:
    #     print(doi)

    # download_link = doi_info("5794107", print_info=False)

    # print(download_link)

    # download_file(download_link[0], filename="data/test.csv")
    print("Main function: started")