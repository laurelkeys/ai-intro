package com.boids

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
    private var maxForce: Float = 0.4f
    private var maxSpeed: Float = 4f

    private var alignmentWeight: Float = 1f
    private var cohesionWeight: Float = 1f
    private var separationWeight: Float = 1.5f

    private var perceptionRadius: Float = 50f // alignmentRadius and cohesionRadius
    private var separationRadius: Float = 25f

    private var showPerceptionRadius = false
    private var showSeparationRadius = false

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
    }

    private fun setupSliders() {
        controller
            .addSlider("Alignment", 0f, 10f, 1f, 10, height - 50, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) alignmentWeight = it.controller.value }

        controller
            .addSlider("Cohesion", 0f, 10f, 1f, 10, height - 35, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) cohesionWeight = it.controller.value }

        controller
            .addSlider("Separation", 0f, 10f, 1.5f, 10, height - 20, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) separationWeight = it.controller.value }

        controller
            .addSlider("Max force", 0f, 2f, 0.4f, width - 190, height - 65, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) maxForce = it.controller.value }

        controller
            .addSlider("Max speed", 0f, 8f, 4f, width - 190, height - 50, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) maxSpeed = it.controller.value }

        val maxRadius = min(width, height) / 2f

        controller
            .addSlider("Perception radius", 0f, maxRadius, 50f, width - 190, height - 35, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) perceptionRadius = it.controller.value }

        controller
            .addSlider("Separation radius", 0f, maxRadius, 25f, width - 190, height - 20, 100, 10)
            .addCallback { if (it.action == ACTION_BROADCAST) separationRadius = it.controller.value }
    }

    override fun draw() {
        background(50)
        flock.run()
    }

    override fun mousePressed() {
        flock.addBoid(Boid(mouseX / 1f, mouseY / 1f))
    }

    inner class Flock {
        private val boids = ArrayList<Boid>()

        fun addBoid(boid: Boid) = boids.add(boid)

        fun run() {
            val snapshot = ArrayList(boids)
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

        fun run(boids: ArrayList<Boid>) {
            flock(boids)
            update()
            wraparound()
            render()
        }

        private fun flock(boids: ArrayList<Boid>) {
            val behavior = steer(boids)
            /*
            applyForce(
                behavior.first.mult(alignmentWeight),
                behavior.second.mult(cohesionWeight),
                behavior.third.mult(separationWeight)
            )
            */
            applyForce(
                fuzzyAlign(boids).mult(alignmentWeight),
                behavior.second.mult(cohesionWeight),
                behavior.third.mult(separationWeight)
            )
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

            pushMatrix() // saves the current coordinate system to the stack

            translate(position.x, position.y)
            rotate(velocity.heading() + PApplet.radians(90f))

            triangle(
                0f, -2 * sizeUnit,
                -sizeUnit, sizeUnit,
                sizeUnit, sizeUnit
            )

            renderRadii()

            popMatrix() // restores the prior coordinate system
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
            val alignment = PVector(0f, 0f)
            for (other in boids) {
                val dist = PVector.dist(position, other.position)
                if (other != this && dist < perceptionRadius && dist > 0) {
                    ControlSystem.compute(
                        distance = dist / perceptionRadius,
                        headingDiff = degrees(PVector.angleBetween(velocity, other.velocity))
                    )
                    val steer = PVector.fromAngle(radians(ControlSystem.headingChange.value.toFloat()))
                    //steer.div(dist * dist)
                    alignment.add(steer)
                }
            }
            return alignment.normalize()
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
}

private fun Float.clip(min: Float, max: Float) = when {
    this < min -> min
    this > max -> max
    else -> this
}

fun main(args: Array<String>) {
    Sketch.run()
}