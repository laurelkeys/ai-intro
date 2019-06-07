package com.boids.metrics

import com.boids.Sketch
import com.google.gson.Gson
import java.io.FileWriter

object MaxDistance {
    private val maxMin: MutableList<Float> = ArrayList()
    private val maxAvg: MutableList<Float> = ArrayList()
    private val maxMax: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val maxDistances = (0 until boids.size - 1).map { i ->
            (i + 1 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]
                val distance = first.position.dist(second.position)

                distance // return the distance between the boids
            }.max() ?: 0f
        }

        maxMin.add(maxDistances.min() ?: Float.MAX_VALUE)
        maxMax.add(maxDistances.max() ?: 0f)
        maxAvg.add(maxDistances.sum() / maxDistances.size)
    }

    fun save() {
        val gson = Gson()

        val maxMinWriter = FileWriter("metrics/maxMin.json")
        val maxMaxWriter = FileWriter("metrics/maxMax.json")
        val maxAvgWriter = FileWriter("metrics/maxAvg.json")

        gson.toJson(maxMin, maxMinWriter)
        gson.toJson(maxMax, maxMaxWriter)
        gson.toJson(maxAvg, maxAvgWriter)

        maxMinWriter.flush()
        maxMinWriter.close()
        maxMaxWriter.flush()
        maxMaxWriter.close()
        maxAvgWriter.flush()
        maxAvgWriter.close()

        maxMin.clear()
        maxMax.clear()
        maxAvg.clear()
    }
}