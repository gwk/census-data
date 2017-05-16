'''
Parse 2015_5yr_Summary_FileTemplates/2015_SFGeoFileTemplate.xls to obtain exact column headers for the ACS geography files.

'''

import xlrd
import csv
from itertools import starmap
from typing import Any, BinaryIO
from muck import add_loader, load
from pithy.io import *
from pithy.json_utils import *


def load_xls(file: BinaryIO) -> Any:
  return xlrd.open_workbook(filename=file.name, logfile=stderr)

add_loader('.xls', load_xls, binary=True)


def main():
  path = f'2015_5yr_Summary_FileTemplates/2015_SFGeoFileTemplate.xls'
  book = load(path)
  sheets = book.sheets()
  assert len(sheets) == 1
  sheet = sheets[0]
  rows = list(sheet.get_rows())
  assert len(rows) == 2
  header = []
  for c0, c1 in zip(*rows):
    name = c0.value
    desc = c1.value
    header.append([name, desc])
  out_json(header)

main()
