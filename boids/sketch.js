// Flocking
// Daniel Shiffman
// https://thecodingtrain.com

// https://thecodingtrain.com/CodingChallenges/124-flocking-boids.html
// https://youtu.be/mhjuuHl6qHM
// https://editor.p5js.org/codingtrain/sketches/ry4XZ8OkN

const flock = [];

let alignSlider, cohesionSlider, separationSlider;

function setup() {
  createCanvas(640, 480);
  

  sDiv = createDiv('Separation');
  separationSlider = createSlider(0, 2, 1, 0.1)
  separationSlider.parent(sDiv)

  aDiv = createDiv('Alignment');
  alignmentSlider = createSlider(0, 2, 1, 0.1);
  alignmentSlider.parent(aDiv)

  cDiv = createDiv('Cohesion');
  cohesionSlider = createSlider(0, 2, 1, 0.1);
  cohesionSlider.parent(cDiv)

  for (let i = 0; i < 200; i++) {
    flock.push(new Boid());
  }
}

function draw() {
  background(51);
  for (let boid of flock) {
    boid.edges();
    boid.flock(flock);
    boid.update();
    boid.show();
  }
}
