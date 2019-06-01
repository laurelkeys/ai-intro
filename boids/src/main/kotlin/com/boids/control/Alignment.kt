package com.boids

import com.fuzzylite.imex.FclImporter
import com.fuzzylite.variable.InputVariable
import com.fuzzylite.variable.OutputVariable
import java.nio.file.Paths

object ControlSystem {

    private val engine = FclImporter().fromFile(
        Paths.get(".", "src", "fcl", "align.fcl").toFile()
    )

    // antecedent
    val distance: InputVariable
    val headingDiff: InputVariable

    // consequent
    val headingChange: OutputVariable

    init {
        val status = StringBuilder()
        if (!engine.isReady(status))
            throw RuntimeException("[engine error] engine is not ready:n$status")

        distance = engine.getInputVariable("dist")
        headingDiff = engine.getInputVariable("hDiff")

        headingChange = engine.getOutputVariable("hChg")
    }

    fun compute(distance: Int, headingDiff: Int) = compute(distance.toDouble(), headingDiff.toDouble())

    fun compute(distance: Float, headingDiff: Float) = compute(distance.toDouble(), headingDiff.toDouble())

    fun compute(distance: Double, headingDiff: Double) {
        this.distance.value = distance
        this.headingDiff.value = headingDiff
        compute()
    }

    fun compute() = engine.process()
}