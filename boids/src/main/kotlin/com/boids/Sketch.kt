package com.boids

import com.boids.control.Brain
import com.boids.extensions.*
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

    private val flock = ArrayList<Boid>()
    private var homeBorder: Float = 0f

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
    private var thinkFuzzy: Boolean = true
    private var wraparound: Boolean = true

    private var chartingRate = 0

    override fun settings() {
        size(displayWidth / 2, displayHeight / 2)
    }

    override fun setup() {
        noFill()
        background(50)

        controller = ControlP5(this)
        setupToggles()
        setupSliders()

        if (SEED_RANDOM) randomSeed(0L)

        homeBorder = 0.1f * min(width, height)
        repeat(flockSize) {
            flock.add(
                Boid(
                    random(homeBorder, width - homeBorder),
                    random(homeBorder, height - homeBorder)
                )
            )
        }
    }

    override fun draw() {
        background(50)
        if (!wraparound) {
            stroke(0f)
            rectMode(CENTER)
            rect(width / 2f, height / 2f, width - 2 * homeBorder, height - 2 * homeBorder)
        }

        stroke(1f)
        if (SHOW_FPS) {
            textSize(18f)
            fill(0f, 116f, 217f)
            text("%.0fFPS".format(frameRate), 5f, 20f)
        }

        run()
    }

    private fun run() {
        val snapshot = flock.map {
            Boid(it.position.x, it.position.y, it.velocity, it.acceleration)
        }

        for (boid in flock) boid.run(snapshot)

        if (PLOTTING) {
            MetricsExecutor.run(flock)
            this.chartingRate++
            if (this.chartingRate > METRICS_CHARTING_RATE) {
                this.chartingRate = 0
                MetricsExecutor.plot()
            }
        }
    }

    inner class Boid(
        x: Float, y: Float,
        var velocity: PVector = PVector.random2D(this@Sketch),
        var acceleration: PVector = PVector(0f, 0f)
    ) {

        var position: PVector = PVector(x, y)

        fun run(boids: List<Boid>) {
            flock(boids) // adds steering forces to the acceleration (Σ F = m * a, with m = 1)
            update()
            if (wraparound) wraparound()
            render()
        }

        private fun flock(boids: List<Boid>) {
            val steeringForces = when {
                thinkFuzzy -> Brain.fuzzySteer(this, boids, perceptionRadius, separationRadius)
                else -> Brain.crispSteer(this, boids, perceptionRadius, separationRadius)
            }
            val alignment = steeringForces.first
            val cohesion = steeringForces.second
            val separation = steeringForces.third

            if (showForces) drawSteeringForces(alignment, cohesion, separation)

            acceleration
                .add(
                    alignment.mult(alignmentWeight),
                    cohesion.mult(cohesionWeight),
                    separation.mult(separationWeight)
                )
                .limit(maxForce)

            if (!wraparound) {
                when {
                    position.x < homeBorder -> acceleration.add(PVector(maxSpeed, velocity.y).sub(velocity).normalize())
                    position.x > width - homeBorder -> acceleration.add(PVector(-maxSpeed, velocity.y).sub(velocity).normalize())
                }
                when {
                    position.y < homeBorder -> acceleration.add(PVector(velocity.x, maxSpeed).sub(velocity).normalize())
                    position.y > height - homeBorder -> acceleration.add(PVector(velocity.x, -maxSpeed).sub(velocity).normalize())
                }
            }
        }

        private fun update() {
            velocity.add(acceleration).limit(maxSpeed)
            position.add(velocity)
            acceleration.mult(0f)
        }

        private fun render() {
            strokeWeight(2f)
            stroke(255)
            pushPop(origin = position, angle = velocity.heading()) {
                triangle(
                    2 * BOID_SIZE_SCALE, 0f,
                    -BOID_SIZE_SCALE, BOID_SIZE_SCALE,
                    -BOID_SIZE_SCALE, -BOID_SIZE_SCALE
                )
                renderRadii()
            }
        }

        private fun renderRadii() {
            noFill()

            if (showPerceptionRadius) {
                stroke(250f, 5f, 110f, 100f)
                circle(radius = perceptionRadius)
            }

            if (showSeparationRadius) {
                stroke(0f, 250f, 250f, 100f)
                circle(radius = separationRadius)
            }
        }

        private fun drawSteeringForces(alignment: PVector, cohesion: PVector, separation: PVector) {
            pushPop(origin = position) {
                stroke(255f, 0f, 0f, 128f) // RED: alignment
                lineTo(BOID_FORCE_SCALE * alignment)

                stroke(0f, 255f, 0f, 128f) // GREEN: cohesion
                lineTo(BOID_FORCE_SCALE * cohesion)

                stroke(0f, 0f, 255f, 128f) // BLUE: separation
                lineTo(BOID_FORCE_SCALE * separation)
            }
        }

        private fun wraparound() {
            when {
                position.x < -BOID_SIZE_SCALE -> position.x = width + BOID_SIZE_SCALE
                position.x > width + BOID_SIZE_SCALE -> position.x = -BOID_SIZE_SCALE
            }
            when {
                position.y < -BOID_SIZE_SCALE -> position.y = height + BOID_SIZE_SCALE
                position.y > height + BOID_SIZE_SCALE -> position.y = -BOID_SIZE_SCALE
            }
        }
    }

    override fun mousePressed() {
        if (mouseButton == RIGHT) {
            flock.add(Boid(mouseX.toFloat(), mouseY.toFloat()))
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

            addToggle(
                name = "Use fuzzy rules",
                label = "fuzzy",
                value = !thinkFuzzy,
                position = width - 50 to 115
            ) { value -> thinkFuzzy = value == 0f }

            addToggle(
                name = "Allow boids to wraparound screen",
                label = "confine",
                value = wraparound,
                position = width - 50 to 150
            ) { value -> wraparound = value != 0f }
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
}

fun main(args: Array<String>) {
    Sketch.run()
}