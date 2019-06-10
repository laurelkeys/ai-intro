package com.boids.metrics

import com.boids.Sketch
import com.google.gson.Gson
import processing.core.PVector
import java.io.FileWriter

object MinDistance {
    private val minmin: MutableList<Float> = ArrayList()
    private val minavg: MutableList<Float> = ArrayList()
    private val maxmin: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val minDistances = (0 until boids.size).map { i ->
            (0 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]
                val distance = PVector.dist(first.position, second.position)

                if (i != j) distance else Float.MAX_VALUE // return the distance between the boids
            }.min() ?: Float.MAX_VALUE
        }

        minmin.add(minDistances.min() ?: Float.MAX_VALUE)
        maxmin.add(minDistances.max() ?: 0f)
        minavg.add(minDistances.sum() / minDistances.size)
    }

    fun save() {
        val gson = Gson()

        val minminWriter = FileWriter("metrics/minmin.json")
        val minavgWriter = FileWriter("metrics/minavg.json")
        val maxminWriter = FileWriter("metrics/maxmin.json")

        gson.toJson(minmin, minminWriter)
        gson.toJson(minavg, minavgWriter)
        gson.toJson(maxmin, maxminWriter)

        minminWriter.flush()
        minminWriter.close()
        minavgWriter.flush()
        minavgWriter.close()
        maxminWriter.flush()
        maxminWriter.close()

        minmin.clear()
        minavg.clear()
        maxmin.clear()
    }
}