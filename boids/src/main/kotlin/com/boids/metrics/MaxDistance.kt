package com.boids.metrics

import com.boids.Sketch
import com.google.gson.Gson
import processing.core.PVector
import java.io.FileWriter

object MaxDistance {
    private val minmax: MutableList<Float> = ArrayList()
    private val maxavg: MutableList<Float> = ArrayList()
    private val maxmax: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val maxDistances = (0 until boids.size).map { i ->
            (0 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]
                val distance = PVector.dist(first.position, second.position)

                if (i != j) distance else 0f // return the distance between the boids
            }.max() ?: 0f
        }

        minmax.add(maxDistances.min() ?: Float.MAX_VALUE)
        maxmax.add(maxDistances.max() ?: 0f)
        maxavg.add(maxDistances.sum() / maxDistances.size)
    }

    fun save() {
        val gson = Gson()

        val minmaxWriter = FileWriter("metrics/minmax.json")
        val maxmaxWriter = FileWriter("metrics/maxmax.json")
        val maxavgWriter = FileWriter("metrics/maxavg.json")

        gson.toJson(minmax, minmaxWriter)
        gson.toJson(maxmax, maxmaxWriter)
        gson.toJson(maxavg, maxavgWriter)

        minmaxWriter.flush()
        minmaxWriter.close()
        maxmaxWriter.flush()
        maxmaxWriter.close()
        maxavgWriter.flush()
        maxavgWriter.close()

        minmax.clear()
        maxmax.clear()
        maxavg.clear()
    }
}