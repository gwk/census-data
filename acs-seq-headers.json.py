
'''
Parse the 2015_5yr_Summary_FileTemplates XLS documents to obtain exact column headers for each of the 122 sequence files.

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
  #verbosity=0,
  #use_mmap=USE_MMAP,
  #file_contents=None,
  #encoding_override=None,
  #formatting_info=False,
  #on_demand=False,
  #ragged_rows=False,

add_loader('.xls', load_xls, binary=True)

template_dir = '2015_5yr_Summary_FileTemplates/2015_5yr_Templates'


def main():
  headers = [None]
  for seq_id in range(1, 123):
    path = f'{template_dir}/Seq{seq_id}.xls'
    errL(path)
    book = load(path)
    sheets = book.sheets()
    assert len(sheets) == 1
    sheet = sheets[0]
    rows = list(sheet.get_rows())
    assert len(rows) == 2
    assert seq_id == len(headers)
    headers.append(list(starmap(agg_column, zip(*rows))))

  out_json(headers)


def agg_column(c0, c1):
  v0 = c0.value
  v1 = c1.value
  if v0 == v1: return v0
  return f'{v0}: {v1}'


main()
