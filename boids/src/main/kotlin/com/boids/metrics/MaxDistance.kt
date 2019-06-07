package com.boids.metrics

import com.boids.Sketch
import org.jfree.chart.ChartFactory
import org.jfree.chart.ChartUtilities
import org.jfree.chart.plot.PlotOrientation
import org.jfree.data.category.DefaultCategoryDataset
import java.io.File

object MaxDistance {
    private val samples: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val maxDistance = (0 until boids.size - 1).map { i ->
            (i + 1 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]

                first.position.dist(second.position) // return the distance between the boids
            }.max() ?: 0f
        }.max() ?: 0f

        samples.add(maxDistance)
    }

    fun plot() {
        val dataset = DefaultCategoryDataset()

        samples.forEachIndexed { index, fl ->
            dataset.addValue(fl, "max", index)
        }

        val chart = ChartFactory.createLineChart(
            "Maximum inner distance",
            "Frame",
            "Distance",
            dataset,
            PlotOrientation.VERTICAL,
            false,
            false,
            false
        )

        val lineChart = File("metrics/Max.jpeg")
        ChartUtilities.saveChartAsJPEG(lineChart, chart, 1000, 500)
    }
}