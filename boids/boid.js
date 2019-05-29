// Flocking
// Daniel Shiffman
// https://thecodingtrain.com/CodingChallenges/124-flocking-boids.html
// https://youtu.be/mhjuuHl6qHM
// https://editor.p5js.org/codingtrain/sketches/ry4XZ8OkN

class Boid {
    
    constructor(maxForce=1, maxSpeed=4, radii=50) {
        this.position = createVector(random(width), random(height));
        this.velocity = p5.Vector.random2D();
        this.velocity.setMag(random(2, 4));
        this.acceleration = createVector();
        this.maxForce = maxForce;
        this.maxSpeed = maxSpeed;
        this.radii = radii; // perception radius
    }
    
    steer(boids) {
        // calculates the steering behaviors
        let alignment = createVector(), cohesion = createVector(), separation = createVector();
        
        let total = 0;
        for (let other of boids) {
            let d = dist(this.position.x, this.position.y, other.position.x, other.position.y);
            if (other != this && d < this.radii) {
                alignment.add(other.velocity);
                cohesion.add(other.position);
                let diff = p5.Vector.sub(this.position, other.position);
                diff.div(d * d);
                separation.add(diff);
                total++;
            }
        }

        let steering = { align: alignment, cohere: cohesion, separate: separation };

        if (total > 0) {
            for (let behavior in steering) steering[behavior].div(total);

            steering['cohere'].sub(this.position);

            for (let behavior in steering) {
                steering[behavior].setMag(this.maxSpeed);
                steering[behavior].sub(this.velocity);
                steering[behavior].limit(this.maxForce);
            }
        }
        
        return steering;
    }
    
    flock(boids) {
        let steering = this.steer(boids);
        let alignment = steering.align;
        let cohesion = steering.cohere;
        let separation = steering.separate;
        
        alignment.mult(alignmentSlider.value());
        cohesion.mult(cohesionSlider.value());
        separation.mult(separationSlider.value());
        
        this.acceleration.add(alignment);
        this.acceleration.add(cohesion);
        this.acceleration.add(separation);
        this.acceleration.limit(this.maxForce); // F = m * a, with m = 1
    }
    
    update() {
        this.position.add(this.velocity);
        this.velocity.add(this.acceleration);
        this.velocity.limit(this.maxSpeed);
        this.acceleration.mult(0);
    }
    
    show() {
        strokeWeight(2);
        stroke(255);
        
        push();
        
        translate(this.position.x, this.position.y);
        rotate(this.velocity.heading() + radians(90));

        let unitLength = 2;
        beginShape();
        vertex(0, -2*unitLength);
        vertex(-unitLength, unitLength);
        vertex(unitLength, unitLength);
        endShape(CLOSE);
        
        pop();
    }
    
    wraparound() {
        if (this.position.x > width) {
            this.position.x = 0;
        } else if (this.position.x < 0) {
            this.position.x = width;
        }
        
        if (this.position.y > height) {
            this.position.y = 0;
        } else if (this.position.y < 0) {
            this.position.y = height;
        }
    }
}
