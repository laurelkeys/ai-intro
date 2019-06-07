package com.boids.metrics

import com.boids.Sketch

object MetricsExecutor {
    fun run(boids: List<Sketch.Boid>) {
        MinimumDistance.sample(boids)
        MaxDistance.sample(boids)
    }

    fun plot() {
        MaxDistance.plot()
        MinimumDistance.plot()
    }
}