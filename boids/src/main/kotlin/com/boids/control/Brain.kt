package com.boids.control

import com.boids.Sketch
import processing.core.PApplet.*
import processing.core.PVector

object Brain {

    fun crispSteer(
        boid: Sketch.Boid,
        flockmates: List<Sketch.Boid>,
        perceptionRadius: Float,
        separationRadius: Float
    ): Triple<PVector, PVector, PVector> {
        val alignment = PVector(0f, 0f)
        val cohesion = PVector(0f, 0f)
        val separation = PVector(0f, 0f)

        var count = 0f
        for (other in flockmates) {
            val dist = PVector.dist(boid.position, other.position)
            if (other != boid && dist < perceptionRadius && dist > 0) {
                ++count
                alignment.add(other.velocity)
                cohesion.add(other.position)
                if (separationRadius > dist)
                    separation.add(
                        PVector
                            .sub(boid.position, other.position) // the separation force is inversely
                            .div(dist * dist)              // proportional to the square of the distance
                    )
            }
        }

        if (count > 0) {
            alignment.div(count)
            alignment.sub(boid.velocity)
            alignment.normalize()

            cohesion.div(count)
            cohesion.sub(boid.position)
            cohesion.normalize()

            separation.normalize()
        }

        return Triple(alignment, cohesion, separation)
    }

    // returns the angle difference value as expected by the fuzzy control system
    private fun angleDiff(from: PVector, to: PVector): Float {
        val dot = from.x * to.x + from.y * to.y
        val det = from.x * to.y - from.y * to.x
        return degrees(atan2(det, dot))
    }

    fun fuzzySteer(
        boid: Sketch.Boid,
        flockmates: List<Sketch.Boid>,
        perceptionRadius: Float,
        separationRadius: Float
    ): Triple<PVector, PVector, PVector> {
        val alignment = PVector(0f, 0f)
        val cohesion = PVector(0f, 0f)
        val separation = PVector(0f, 0f)

        var count = 0f
        for (other in flockmates) {
            if (other != boid) {
                ++count
                val distVector = PVector.sub(other.position, boid.position)
                distVector.mag().let { dist ->
                    if (0 < dist && dist <= perceptionRadius) {
                        Alignment.evaluate(
                            dist / perceptionRadius,
                            angleDiff(boid.velocity, other.velocity)
                        )
                        alignment.add(
                            PVector
                                .fromAngle(boid.velocity.heading())
                                .rotate(radians(Alignment.headingChange.value.toFloat()))
                        )

                        Cohesion.evaluate(
                            dist / perceptionRadius,
                            angleDiff(boid.velocity, distVector)
                        )
                        cohesion.add(
                            PVector
                                .fromAngle(boid.velocity.heading())
                                .rotate(radians(Cohesion.headingChange.value.toFloat()))
                        )

                        if (dist <= separationRadius) {
                            Separation.evaluate(
                                dist / separationRadius,
                                angleDiff(boid.velocity, distVector)
                            )
                            separation.add(
                                PVector
                                    .fromAngle(boid.velocity.heading())
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
}