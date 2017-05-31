
const pi2 = Math.PI * 2;

const log = console.log;


function load() {
  // main program setup.
  log('loading...');

  // set up the canvas context and initialize size variables.
  let canvas = document.getElementById('canvas');
  let ctx = canvas.getContext('2d');
  let {width: w, height: h} = canvas.getBoundingClientRect();
  let scaleFactor = screenScaleFactor();

  log(`canvas: ${w} ${h} scale:${scaleFactor}`);

  canvas.width = w * scaleFactor;
  canvas.height = h * scaleFactor;
  ctx.scale(scaleFactor, scaleFactor); // scale the rendering context for high-res displays.
  log(`canvas w:${canvas.width} h:${canvas.height}`);


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

  function render(dots) {
    log("RENDER");
    for (let [nx, ny, nr, color] of dots) {
      ctx.fillStyle = color;
      let x = nx * w;
      let y = ny * w;
      let r = nr * 12;
      //log(`${x} ${y} ${r} ${color}`);
      fill_circle(x, y, r, color);
    }
  }

  fetch("_build/acs-pop-dots.json")
    .then(response => response.json())
    .then(json => render(json))
    .catch(error => console.error(error));
}


function screenScaleFactor() {
  // detect if the screen is a retina display.
  if ('devicePixelRatio' in window) {
    if (window.devicePixelRatio > 1) {
      return window.devicePixelRatio;
    }
  }
  return 1;
}
