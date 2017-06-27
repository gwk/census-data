'use strict';

const pi2 = Math.PI * 2;

const log = console.log;


function load() {
  // main program setup.

  let data = {
    dots: null,
  };

  let ctx = canvas.getContext('2d');

  window.onresize = ()=>{
    let {width: w, height: h} = canvas.getBoundingClientRect();
    let scaleFactor = screenScaleFactor();
    log(`resize: w:${w} h:${h} scale:${scaleFactor}`)
    canvas.width = w * scaleFactor;
    canvas.height = h * scaleFactor;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(scaleFactor, scaleFactor); // scale the rendering context for high-res displays.
    ctx.scale(w, w); // scale to normalized coordinates by width, maintaining aspect ratio.
    render()
  }

  window.onresize() // perform initial size.

  function radiusAction() {
    radiusVal.value = radiusSlider.value;
    render();
  }
  radiusSlider.addEventListener("input", radiusAction, false);
  radiusAction() // initial update.


  // fetch data.
  fetch("_build/acs-pop-dots.json")
    .then(response => response.json())
    .then(json => {
      data.dots = json;
      render();
    })
    .catch(error => console.error(error));

  function render() {
    ctx.clearRect(0, 0, 1, 1);
    if (data.dots == null) { return; }
    let radiusScale = radiusSlider.value;
    let {width: w, height: h} = canvas.getBoundingClientRect();
    for (let [nx, ny, nr, color] of data.dots) {
      ctx.fillStyle = color;
      let x = nx;
      let y = ny;
      let r = nr * 0.001 * radiusScale;
      //log(`${x} ${y} ${r} ${color}`);
      fill_circle(x, y, r, color);
    }
  }

  function draw_line(x0, y0, x1, y1) {
    // convenience function to draw a single line.
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.closePath();
    ctx.stroke();
  }

  function stroke_circle(x, y, radius) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, pi2, true);
    ctx.closePath();
    ctx.stroke();
  }

  function fill_circle(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, pi2, true);
    ctx.closePath();
    ctx.fill();
  }
}


function screenScaleFactor() {
  // detect if the screen is a retina display.
  if ('devicePixelRatio' in window && window.devicePixelRatio > 1) {
    return window.devicePixelRatio;
  }
  return 1;
}
