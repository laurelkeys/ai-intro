package com.boids.control

import com.fuzzylite.imex.FclImporter
import com.fuzzylite.variable.InputVariable
import com.fuzzylite.variable.OutputVariable
import java.nio.file.Paths

object Cohesion {

    private val engine = FclImporter().fromFile(
        Paths.get(".", "src", "fcl", "cohere.fcl").toFile()
    )

    // antecedent
    val distance: InputVariable
    val positionDiff: InputVariable

    // consequent
    val headingChange: OutputVariable

    init {
        val status = StringBuilder()
        if (!engine.isReady(status))
            throw RuntimeException("[engine error] engine is not ready:\n$status")

        distance = engine.getInputVariable("dist")
        positionDiff = engine.getInputVariable("pDiff")

        headingChange = engine.getOutputVariable("hChg")
    }

    fun compute(distance: Int, positionDiff: Int) =
        compute(distance.toDouble(), positionDiff.toDouble())

    fun compute(distance: Float, positionDiff: Float) =
        compute(distance.toDouble(), positionDiff.toDouble())

    fun compute(distance: Double, positionDiff: Double) {
        Cohesion.distance.value = distance
        Cohesion.positionDiff.value = positionDiff
        compute()
    }

    fun compute() = engine.process()
}