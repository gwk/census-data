
'''
Parse the 2015_5yr_Summary_FileTemplates XLS documents to obtain exact column headers for each of the 122 sequence files.

'''

from itertools import starmap
from muck import *
from pithy.io import *
from pithy.json_utils import *


template_dir = '2015_5yr_Summary_FileTemplates/2015_5yr_Templates'


def main():
  headers = {}
  for archive_file in load('data/2015_5yr_Summary_FileTemplates.zip'):
    errL(archive_file)
    m = re.match(r'2015_5yr_Templates/Seq(\d+).xls', archive_file.name)
    if not m: continue # skip the geo file.
    seq_id = int(m[1])
    book = load(archive_file)
    sheets = book.sheets()
    assert len(sheets) == 1
    sheet = sheets[0]
    rows = list(sheet.get_rows())
    assert len(rows) == 2
    headers[seq_id] = list(starmap(agg_column, zip(*rows)))
  assert len(headers) == 122
  header_list = [headers.get(i) for i in range(123)]
  out_json(header_list)


def agg_column(c0, c1):
  'Assemble a colum name from the two cells.'
  v0 = c0.value
  v1 = c1.value
  if v0 == v1: return v0
  return f'{v0}: {v1}'


main()
