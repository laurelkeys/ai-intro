package com.boids.metrics

import com.boids.Sketch
import org.jfree.chart.ChartFactory
import org.jfree.chart.ChartUtilities
import org.jfree.chart.plot.PlotOrientation
import org.jfree.data.category.DefaultCategoryDataset
import java.io.File

object MinimumDistance {
    val samples: MutableList<Float> = ArrayList()

    fun sample(boids: List<Sketch.Boid>) {
        val minDistance = (0 until boids.size - 1).map { i ->
            (i + 1 until boids.size).map { j ->
                val first = boids[i]
                val second = boids[j]

                first.position.dist(second.position) // return the distance between the boids
            }.min() ?: Float.MAX_VALUE
        }.min() ?: Float.MAX_VALUE

        samples.add(minDistance)
    }

    fun plot() {
        val dataset = DefaultCategoryDataset()

        samples.forEachIndexed { index, fl ->
            dataset.addValue(fl, "min", index)
        }

        val chart = ChartFactory.createLineChart(
            "Minimum inner distance",
            "Frame",
            "Distance",
            dataset,
            PlotOrientation.VERTICAL,
            false,
            false,
            false
        )

        val lineChart = File("metrics/Minimum.jpeg")
        ChartUtilities.saveChartAsJPEG(lineChart, chart, 1000, 500)
    }
}