'''
Parse 2015_5yr_Summary_FileTemplates/2015_SFGeoFileTemplate.xls to obtain exact column headers for the ACS geography files.

'''

from muck import *
from pithy.io import *
from pithy.json_utils import *


def main():
  book = load('data/2015_5yr_Summary_FileTemplates.zip', single_name='2015_SFGeoFileTemplate.xls')
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
