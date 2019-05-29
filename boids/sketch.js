// Flocking
// Daniel Shiffman
// https://thecodingtrain.com

// https://thecodingtrain.com/CodingChallenges/124-flocking-boids.html
// https://youtu.be/mhjuuHl6qHM
// https://editor.p5js.org/codingtrain/sketches/ry4XZ8OkN

const boids = [];

let alignSlider, cohesionSlider, separationSlider;

function setup() {
    createCanvas(640, 480);
    
    aDiv = createDiv('Alignment');
    alignmentSlider = createSlider(0, 2, 1, 0.1);
    alignmentSlider.parent(aDiv)
    
    cDiv = createDiv('Cohesion');
    cohesionSlider = createSlider(0, 2, 1, 0.1);
    cohesionSlider.parent(cDiv)
    
    sDiv = createDiv('Separation');
    separationSlider = createSlider(0, 2, 1, 0.1)
    separationSlider.parent(sDiv)
    
    for (let i = 0; i < 200; i++) {
        boids.push(new Boid());
    }
}

function draw() {
    background(51);
    let boidsSnapshot = [...boids];
    for (let boid of boids) {
        boid.flock(boidsSnapshot);
        boid.update();
        boid.wraparound();
        boid.show();
    }
}
