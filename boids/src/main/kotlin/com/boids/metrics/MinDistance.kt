package com.boids.metrics

import com.boids.Sketch
import com.google.gson.Gson
import java.io.FileWriter

object MinDistance {
    private val minMin: MutableList<Float> = ArrayList()
    private val minAvg: MutableList<Float> = ArrayList()
    private val minMax: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val minDistances = (0 until boids.size - 1).map { i ->
            (i + 1 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]
                val distance = first.position.dist(second.position)

                distance // return the distance between the boids
            }.min() ?: Float.MAX_VALUE
        }

        minMin.add(minDistances.min() ?: Float.MAX_VALUE)
        minMax.add(minDistances.max() ?: 0f)
        minAvg.add(minDistances.sum() / minDistances.size)
    }

    fun save() {
        val gson = Gson()

        val minMinWriter = FileWriter("metrics/minMin.json")
        val minAvgWriter = FileWriter("metrics/minAvg.json")
        val minMaxWriter = FileWriter("metrics/minMax.json")

        gson.toJson(minMin, minMinWriter)
        gson.toJson(minAvg, minAvgWriter)
        gson.toJson(minMax, minMaxWriter)

        minMinWriter.flush()
        minMinWriter.close()
        minAvgWriter.flush()
        minAvgWriter.close()
        minMaxWriter.flush()
        minMaxWriter.close()

        minMin.clear()
        minAvg.clear()
        minMax.clear()
    }
}