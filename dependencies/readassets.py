import os
from bs4 import BeautifulSoup


def get_xml_data(file, keyword):
    """Returns a ResultSet containing all instances of the given keyword in the given file"""
    currentdir = os.getcwd()

    return BeautifulSoup(
        open(rf"{currentdir}\\{file}", 'r', encoding='UTF-8').read(), "xml"
    ).find_all(keyword)
