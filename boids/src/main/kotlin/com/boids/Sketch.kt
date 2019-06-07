package com.boids

import com.boids.Settings.ALIGNMENT_WEIGHT
import com.boids.Settings.COHESION_WEIGHT
import com.boids.Settings.FLOCK_SIZE
import com.boids.Settings.MAX_FORCE
import com.boids.Settings.MAX_SPEED
import com.boids.Settings.METRICS_CHARTING_RATE
import com.boids.Settings.PERCEPTION_RADIUS
import com.boids.Settings.PLOTTING
import com.boids.Settings.SEED_RANDOM
import com.boids.Settings.SEPARATION_RADIUS
import com.boids.Settings.SEPARATION_WEIGHT
import com.boids.Settings.SHOW_FORCES
import com.boids.Settings.SHOW_FPS
import com.boids.Settings.SHOW_PERCEPTION_RADIUS
import com.boids.Settings.SHOW_SEPARATION_RADIUS
import com.boids.control.Alignment
import com.boids.control.Cohesion
import com.boids.control.Separation
import com.boids.extensions.addSlider
import com.boids.extensions.addToggle
import com.boids.extensions.pushPop
import com.boids.extensions.random
import com.boids.metrics.MetricsExecutor
import controlP5.ControlP5
import processing.core.PApplet
import processing.core.PVector

class Sketch(private val flockSize: Int) : PApplet() {

    companion object {
        fun run(flockSize: Int = FLOCK_SIZE) {
            val sketch = Sketch(flockSize)
            sketch.runSketch()
        }
    }

    private lateinit var controller: ControlP5

    private val flock = Flock()

    private var maxForce: Float = MAX_FORCE
    private var maxSpeed: Float = MAX_SPEED

    private var alignmentWeight: Float = ALIGNMENT_WEIGHT
    private var cohesionWeight: Float = COHESION_WEIGHT
    private var separationWeight: Float = SEPARATION_WEIGHT

    private var perceptionRadius: Float = PERCEPTION_RADIUS
    private var separationRadius: Float = SEPARATION_RADIUS

    private var showPerceptionRadius: Boolean = SHOW_PERCEPTION_RADIUS
    private var showSeparationRadius: Boolean = SHOW_SEPARATION_RADIUS
    private var showForces: Boolean = SHOW_FORCES

    private var chartingRate = 0

    override fun settings() {
        size(displayWidth / 2, displayHeight / 2)
    }

    override fun setup() {
        controller = ControlP5(this)

        setupToggles()
        setupSliders()

        if (SEED_RANDOM) randomSeed(0L)

        repeat(flockSize) {
            flock.addBoid(
                Boid(random(width), random(height))
            )
        }
    }

    private fun setupToggles() {
        with(controller) {
            addToggle(
                name = "Show perception radius",
                label = "perception",
                value = !showPerceptionRadius,
                position = width - 50 to 10
            ) { value -> showPerceptionRadius = value == 0f }

            addToggle(
                name = "Show separation radius",
                label = "separation",
                value = !showSeparationRadius,
                position = width - 50 to 45
            ) { value -> showSeparationRadius = value == 0f }

            addToggle(
                name = "Show steering forces",
                label = "forces",
                value = !showForces,
                position = width - 50 to 80
            ) { value -> showForces = value == 0f }
        }
    }

    private fun setupSliders() {
        with(controller) {
            addSlider("Alignment", max = 10, default = alignmentWeight, position = 10 to height - 50)
            { value -> alignmentWeight = value }

            addSlider("Cohesion", max = 10, default = cohesionWeight, position = 10 to height - 35)
            { value -> cohesionWeight = value }

            addSlider("Separation", max = 10, default = separationWeight, position = 10 to height - 20)
            { value -> separationWeight = value }

            addSlider("Max force", max = 2, default = maxForce, position = width - 190 to height - 65)
            { value -> maxForce = value }

            addSlider("Max speed", max = 8, default = maxSpeed, position = width - 190 to height - 50)
            { value -> maxSpeed = value }

            val maxRadius = min(width, height) / 2f

            addSlider("Perception radius", maxRadius, default = perceptionRadius, position = width - 190 to height - 35)
            { value -> perceptionRadius = value }

            addSlider("Separation radius", maxRadius, default = separationRadius, position = width - 190 to height - 20)
            { value -> separationRadius = value }
        }
    }

    override fun draw() {
        background(50)

        if (SHOW_FPS) {
            textSize(18f)
            fill(0f, 116f, 217f)
            text("%.0fFPS".format(frameRate), 5f, 20f)
        }

        flock.run()

        if (PLOTTING) {
            this.chartingRate++
            if (this.chartingRate > METRICS_CHARTING_RATE) {
                this.chartingRate = 0
                MetricsExecutor.plot()
            }
        }
    }

    override fun mousePressed() {
        if (mouseButton == RIGHT) {
            flock.addBoid(Boid(mouseX.toFloat(), mouseY.toFloat()))
        }
    }

    inner class Flock(private val boids: MutableList<Boid> = ArrayList()) {

        fun addBoid(boid: Boid) = boids.add(boid)

        fun run() {
            if (PLOTTING) MetricsExecutor.run(boids)
            val snapshot = boids.map { Boid(it.position.x, it.position.y, it.velocity, it.acceleration) }
            for (boid in boids) boid.run(snapshot)
        }
    }

    inner class Boid(
        x: Float, y: Float,
        var velocity: PVector = PVector.random2D(this@Sketch),
        var acceleration: PVector = PVector(0f, 0f),
        private val sizeUnit: Float = 2f
    ) {

        var position: PVector = PVector(x, y)
        private var forceScale = 40f // vector drawing scaling

        fun run(boids: List<Boid>) {
            flock(boids)
            update()
            wraparound()
            render()
        }

        private fun flock(boids: List<Boid>) {
            val behavior = fuzzySteer(boids) //steer(boids)
            val alignment = behavior.first
            val cohesion = behavior.second
            val separation = behavior.third

            if (showForces) drawSteeringForces(alignment, cohesion, separation)

            applyForce(
                alignment.mult(alignmentWeight),
                cohesion.mult(cohesionWeight),
                separation.mult(separationWeight)
            )
        }

        private fun drawSteeringForces(alignment: PVector, cohesion: PVector, separation: PVector) {
            pushPop(origin = position) {
                // RED: alignment
                stroke(255f, 0f, 0f, 128f)
                line(0f, 0f, forceScale * alignment.x, forceScale * alignment.y)
                // GREEN: cohesion
                stroke(0f, 255f, 0f, 128f)
                line(0f, 0f, forceScale * cohesion.x, forceScale * cohesion.y)
                // BLUE: separation
                stroke(0f, 0f, 255f, 128f)
                line(0f, 0f, forceScale * separation.x, forceScale * separation.y)
            }
        }

        private fun applyForce(vararg force: PVector) {
            force.forEach { acceleration.add(it) } // Σ F = m * a, with m = 1
            acceleration.limit(maxForce)
        }

        private fun update() {
            velocity.add(acceleration).limit(maxSpeed)
            position.add(velocity)
            acceleration.mult(0f)
        }

        private fun wraparound() {
            when {
                position.x < -sizeUnit -> position.x = width + sizeUnit
                position.x > width + sizeUnit -> position.x = -sizeUnit
            }
            when {
                position.y < -sizeUnit -> position.y = height + sizeUnit
                position.y > height + sizeUnit -> position.y = -sizeUnit
            }
        }

        private fun render() {
            strokeWeight(2f)
            stroke(255)
            pushPop(origin = position, angle = velocity.heading()) {
                triangle(
                    2 * sizeUnit, 0f,
                    -sizeUnit, sizeUnit,
                    -sizeUnit, -sizeUnit
                )
                renderRadii()
            }
        }

        private fun renderRadii() {
            noFill()

            if (showPerceptionRadius) {
                stroke(250f, 5f, 110f, 100f)
                ellipse(0f, 0f, perceptionRadius, perceptionRadius)
            }

            if (showSeparationRadius) {
                stroke(0f, 250f, 250f, 100f)
                ellipse(0f, 0f, separationRadius, separationRadius)
            }
        }

        private fun fuzzySteer(boids: List<Boid>): Triple<PVector, PVector, PVector> {
            val alignment = PVector(0f, 0f)
            val cohesion = PVector(0f, 0f)
            val separation = PVector(0f, 0f)

            var count = 0f
            for (other in boids) {
                if (other != this) {
                    ++count
                    val distVector = PVector.sub(other.position, position)
                    distVector.mag().let { dist ->
                        if (0 < dist && dist <= perceptionRadius) {
                            Alignment.evaluate(
                                dist / perceptionRadius,
                                angleDiff(velocity, other.velocity)
                            )
                            alignment.add(
                                PVector
                                    .fromAngle(velocity.heading())
                                    .rotate(radians(Alignment.headingChange.value.toFloat()))
                            )

                            Cohesion.evaluate(
                                dist / perceptionRadius,
                                angleDiff(velocity, distVector)
                            )
                            cohesion.add(
                                PVector
                                    .fromAngle(velocity.heading())
                                    .rotate(radians(Cohesion.headingChange.value.toFloat()))
                            )

                            if (dist <= separationRadius) {
                                Separation.evaluate(
                                    dist / separationRadius,
                                    angleDiff(velocity, distVector)
                                )
                                separation.add(
                                    PVector
                                        .fromAngle(velocity.heading())
                                        .rotate(radians(Separation.headingChange.value.toFloat()))
                                        .div(dist * dist) // TODO use fuzzy logic to calculate the proportionality
                                )
                            }
                        }
                    }
                }
            }

            return Triple(alignment.normalize(), cohesion.normalize(), separation.normalize())
        }

        private fun steer(boids: List<Boid>): Triple<PVector, PVector, PVector> {
            val alignment = PVector(0f, 0f)
            val cohesion = PVector(0f, 0f)
            val separation = PVector(0f, 0f)

            var count = 0f
            for (other in boids) {
                val dist = PVector.dist(position, other.position)
                if (other != this && dist < perceptionRadius && dist > 0) {
                    ++count
                    alignment.add(other.velocity)
                    cohesion.add(other.position)
                    if (separationRadius > dist)
                        separation.add(
                            PVector
                                .sub(position, other.position) // the separation force is inversely
                                .div(dist * dist)              // proportional to the square of the distance
                        )
                }
            }

            if (count > 0) {
                alignment.div(count)
                alignment.sub(velocity)
                alignment.normalize()

                cohesion.div(count)
                cohesion.sub(position)
                cohesion.normalize()

                separation.normalize()
            }

            return Triple(alignment, cohesion, separation)
        }
    }

    // returns the angle difference value as expected by the fuzzy control system
    private fun angleDiff(from: PVector, to: PVector): Float {
        val dot = from.x * to.x + from.y * to.y // dot product between [x1, y1] and [x2, y2]
        val det = from.x * to.y - from.y * to.x // determinant
        return degrees(atan2(det, dot)) // atan2(y, x) or atan2(sin, cos)
    }
}

fun main(args: Array<String>) {
    Sketch.run()
}