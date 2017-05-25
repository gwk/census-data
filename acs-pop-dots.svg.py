from muck import *
from math import log2, sqrt
from typing import NamedTuple
from pithy.io import *
from pithy.immutable import Immutable
from pithy.iterable import min_max, count_by_pred
from muck.pithy.svg import SvgWriter

from headers import geo_pop_header

excluded_states = {
  'AK',
  'HI',
  'GU',
  'PR',
  'VI',
}


class Dot(NamedTuple):
  pop: float
  area: float
  lat: float
  lon: float

  @property
  def pop_density(self) -> float:
    if self.pop == 0: return 0
    return self.pop / self.area


def main():
  'since both datasets come sorted by LOGRECNO, we can simply parse them lazily and zip to join them.'
  dots = []
  for row in err_progress(load('acs-geo-pop-tracts.csv', header=geo_pop_header)):
    spot = Immutable(*zip(geo_pop_header, row))
    assert spot.BLKGRP == '', spot # acs-pop-tracts skips blockgroups because we do not yet have geo data.
    if spot.ALAND == '':
      continue
    if spot.STUSAB in excluded_states: continue
    if spot.STUSAB != 'CA': continue
    dots.append(mk_dot(spot))
  render(dots)


def mk_dot(spot):
  try:
    return Dot(
      pop=float(spot.POPULATION),
      area=float(spot.ALAND),
      lat=float(spot.INTPTLAT),
      lon=float(spot.INTPTLONG))
  except Exception as e:
    errSL('spot:', spot)
    raise


def render(dots):
  errSL('dots:', len(dots))
  pop_min, pop_max = min_max(d.pop for d in dots)
  area_min, area_max = min_max(d.area for d in dots)
  dens_min, dens_max = min_max(filter(None, (d.pop_density for d in dots)))
  errL(f'pop: {pop_min} ... {pop_max}')
  errL(f'area: {area_min} ... {area_max}')
  errL(f'density (excluding zeros): {dens_min} ... {dens_max}; min sq m per person: {1/dens_max}')

  zero_pops   = count_by_pred(dots, lambda d: d.pop == 0)
  zero_areas  = count_by_pred(dots, lambda d: d.area == 0)
  errL(f'zero pop: {zero_pops}; zero area: {zero_areas}')

  dens_lin_scale = 2 / dens_min # want minimum observed density to have a log2 value of 1.
  dens_log_scale = 1 / log2(dens_max * dens_lin_scale) # want max observed density to be 1 on the log2 scale.

  x_min = min(d.lon for d in dots)
  x_max = max(d.lon for d in dots)
  y_min = min(d.lat for d in dots)
  y_max = max(d.lat for d in dots)

  size_x = x_max - x_min
  size_y = y_max - y_min

  margin = 1/16
  mx = margin * size_x
  my = margin * size_y
  ox = x_min - mx
  oy = y_min - my
  w = size_x + mx * 2
  h = size_y + my * 2
  ar = w / h
  errL(f'w = {w}; {x_min} ... {x_max}')
  errL(f'h = {h}; {y_min} ... {y_max}')
  errL(f'ar: {ar}')


  nh = h / w
  errSL('nh:', nh)
  l = 1024
  max_rad = 16

  def pos(dot):
    nx = (dot.lon - ox) / w
    ny = (h - (dot.lat - oy)) / w  # flip y, then normalize by w.
    return (l * nx, l * ny)

  def radius(dot):
    return max_rad * sqrt(dot.area / area_max)

  def color(dot):
    d = dot.pop_density
    if d == 0:
      g = 0
    else:
      v = log2(d * dens_lin_scale) * dens_log_scale
      g = int(round(255 * v))
    return f'#00{g:2x}00'

  with SvgWriter(w=l, h=l*nh) as f:
    f.rect(x=0, y=0, w=l, h=l*nh, fill='black')
    for dot in err_progress(dots):
      f.circle(pos=pos(dot), r=radius(dot), fill=color(dot), stroke=None)

main()
