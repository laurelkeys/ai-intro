package com.boids.metrics

import com.boids.Sketch
import org.jfree.chart.ChartFactory
import org.jfree.chart.ChartUtilities
import org.jfree.chart.plot.PlotOrientation
import org.jfree.data.category.DefaultCategoryDataset
import java.io.File
import com.google.gson.Gson
import java.io.FileWriter


object MinDistance {
    private val minmin: MutableList<Float> = ArrayList()
    private val minavg: MutableList<Float> = ArrayList()
    private val maxmin: MutableList<Float> = ArrayList()



    fun sample(boids: List<Sketch.Boid>) {
        val minDistances = (0 until boids.size - 1).map { i ->
            (i + 1 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]
                val distance = first.position.dist(second.position)

                distance // return the distance between the boids
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