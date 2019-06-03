package com.boids

import com.boids.control.Cohesion
import com.boids.control.Separation
import controlP5.ControlP5
import controlP5.ControlP5Constants.ACTION_BROADCAST
import processing.core.PApplet
import processing.core.PVector
import java.util.ArrayList

fun PApplet.random(high: Int) = random(high.toFloat())

class Sketch(private val boidsCount: Int) : PApplet() {
    companion object {
        fun run(boidsCount: Int = 50) {
            val sketch = Sketch(boidsCount)
            sketch.runSketch()
        }
    }

    private lateinit var controller: ControlP5

    private val flock = Flock()
    private var maxForce: Float = 0.6f
    private var maxSpeed: Float = 2f

    private var alignmentWeight: Float = 0.3f
    private var cohesionWeight: Float = 1.2f
    private var separationWeight: Float = 1.25f

    private var perceptionRadius: Float = 80f // alignmentRadius and cohesionRadius
    private var separationRadius: Float = 30f

    private var showPerceptionRadius = false
    private var showSeparationRadius = false
    private var showForces = false

    override fun settings() {
        size(displayWidth / 2, displayHeight / 2)
    }

    override fun setup() {
        controller = ControlP5(this)
        setupToggles()
        setupSliders()
        repeat(boidsCount) {
            flock.addBoid(
                Boid(random(width), random(height))
            )
        }
    }

    private fun setupToggles() {
        controller
            .addToggle("Show perception radius")
            .setLabel("perception")
            .setPosition(width - 50f, 10f)
            .setSize(40, 10)
            .setValue(!showPerceptionRadius)
            .setMode(ControlP5.SWITCH)
            .addCallback { if (it.action == ACTION_BROADCAST) showPerceptionRadius = it.controller.value == 0f }

        controller
            .addToggle("Show separation radius")
            .setLabel("separation")
            .setPosition(width - 50f, 45f)
            .setSize(40, 10)
            .setValue(!showSeparationRadius)
            .setMode(ControlP5.SWITCH)
            .addCallback { if (it.action == ACTION_BROADCAST) showSeparationRadius = it.controller.value == 0f }

        controller
            .addToggle("Show steering forces")
            .setLabel("forces")
            .setPosition(width - 50f, 80f)
            .setSize(40, 10)
            .setValue(!showForces)
            .setMode(ControlP5.SWITCH)
            .addCallback { if (it.action == ACTION_BROADCAST) showForces = it.controller.value == 0f }
    }

    private fun setupSliders() {
        controller
            .addSlider("Alignment", 0f, 10f, alignmentWeight, 10, height - 50, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) alignmentWeight = it.controller.value }

        controller
            .addSlider("Cohesion", 0f, 10f, cohesionWeight, 10, height - 35, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) cohesionWeight = it.controller.value }

        controller
            .addSlider("Separation", 0f, 10f, separationWeight, 10, height - 20, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) separationWeight = it.controller.value }

        controller
            .addSlider("Max force", 0f, 2f, maxForce, width - 190, height - 65, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) maxForce = it.controller.value }

        controller
            .addSlider("Max speed", 0f, 8f, maxSpeed, width - 190, height - 50, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) maxSpeed = it.controller.value }

        val maxRadius = min(width, height) / 2f

        controller
            .addSlider("Perception radius", 0f, maxRadius, perceptionRadius, width - 190, height - 35, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) perceptionRadius = it.controller.value }

        controller
            .addSlider("Separation radius", 0f, maxRadius, separationRadius, width - 190, height - 20, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) separationRadius = it.controller.value }
    }

    override fun draw() {
        background(50)
        flock.run()
    }

    override fun mousePressed() {
        if (mouseButton == RIGHT) {
            flock.addBoid(Boid(mouseX.toFloat(), mouseY.toFloat()))
        }
    }

    inner class Flock(private val boids: ArrayList<Boid> = ArrayList()) {

        fun addBoid(boid: Boid) = boids.add(boid)

        fun run() {
            val snapshot = ArrayList(boids.map { Boid(it.position.x, it.position.y, it.velocity, it.acceleration) })
            for (boid in boids) boid.run(snapshot)
        }
    }

    inner class Boid(
        x: Float, y: Float,
        var velocity: PVector = PVector.random2D(),
        var acceleration: PVector = PVector(0f, 0f),
        private val sizeUnit: Float = 2f
    ) {
        var position: PVector = PVector(x, y)
        private var forceScale = 40f // vector drawing scaling

        fun run(boids: ArrayList<Boid>) {
            flock(boids)
            update()
            wraparound()
            render()
        }

        private fun flock(boids: ArrayList<Boid>) {
            val behavior = steer(boids)

            val alignment = behavior.first
            val cohesion = behavior.second //fuzzyCohere(boids)
            val separation = behavior.third //fuzzySeparate(boids)
            if (showForces) drawSteeringForces(alignment, cohesion, separation)

            applyForce(
                alignment.mult(alignmentWeight),
                cohesion.mult(cohesionWeight),
                separation.mult(separationWeight)
            )
        }

        private fun drawSteeringForces(alignment: PVector, cohesion: PVector, separation: PVector) {
            pushPop(position.x, position.y) {
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
            pushPop(position.x, position.y, velocity.heading()) {
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

        private fun fuzzyAlign(boids: ArrayList<Boid>): PVector {
//            val alignment = PVector(0f, 0f)
//            var count = 0
//            for (other in boids) {
//                val dist = PVector.dist(position, other.position)
//                if (other != this && dist <= perceptionRadius && dist > 0) {
//                    ++count
//                    Alignment.compute(
//                        distance = dist / perceptionRadius,
//                        headingDiff = angleDiff(velocity, other.velocity)
//                    )
//                    val steer = PVector
//                        .fromAngle(velocity.heading())
//                        .rotate(-radians(Alignment.headingChange.value.toFloat())) // rotates counterclockwise
//                    alignment.add(steer.div(dist * dist)) // NOTE might want to divide steer by dist*dist before adding
//                }
//            }
//            if (count > 0) alignment.sub(velocity)
//            return alignment.normalize()
            return PVector(0f, 0f)
        }

        private fun fuzzyCohere(boids: ArrayList<Boid>): PVector {
            val cohesion = PVector(0f, 0f)
            var count = 0f
            for (other in boids) {
                if (other != this) {
                    ++count
                    val distVector = PVector.sub(other.position, position)
                    distVector.mag().let { dist ->
                        if (0 < dist && dist <= perceptionRadius) {
                            Cohesion.evaluate(
                                dist / perceptionRadius,
                                angleDiff(velocity, distVector)
                            )
                            cohesion.add(
                                PVector
                                    .fromAngle(velocity.heading())
                                    .rotate(radians(Cohesion.headingChange.value.toFloat()))
                            )
                        }
                    }
                }
            }
            if (count == 0f) cohesion.set(velocity) // keeps the same heading direction
            return cohesion.normalize()
        }

        private fun fuzzySeparate(boids: ArrayList<Boid>): PVector {
            val separation = PVector(0f, 0f)
            var count = 0f
            for (other in boids) {
                if (other != this) {
                    ++count
                    val distVector = PVector.sub(other.position, position)
                    distVector.mag().let { dist ->
                        if (0 < dist && dist <= separationRadius) {
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
            if (count == 0f) separation.set(velocity) // keeps the same heading direction
            return separation.normalize()
        }

        private fun steer(boids: ArrayList<Boid>): Triple<PVector, PVector, PVector> {
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

private fun PApplet.pushPop(origin: PVector, angle: Float = 0f, transformation: () -> Unit) {
    pushPop(origin.x, origin.y, angle, transformation)
}

private fun PApplet.pushPop(x: Float = 0f, y: Float = 0f, angle: Float = 0f, transformation: () -> Unit) {
    pushMatrix() // saves the current coordinate system to the stack
    translate(x, y)
    rotate(angle)

    transformation()

    popMatrix() // restores the prior coordinate system
}

fun main(args: Array<String>) {
    Sketch.run()
}