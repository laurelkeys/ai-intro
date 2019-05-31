package com.boids

import com.fuzzylite.imex.FclImporter
import com.fuzzylite.variable.InputVariable
import com.fuzzylite.variable.OutputVariable
import java.io.File
import java.io.File.separatorChar

object AlignmentControl {
    private val engine = FclImporter().fromFile(
        File(".${separatorChar}src${separatorChar}fcl${separatorChar}alignment.fcl")
    )

    // antecedent
    val distance: InputVariable
    val headingDiff: InputVariable
    val speedDiff: InputVariable

    // consequent
    val headingChange: OutputVariable
    val speedChange: OutputVariable

    init {
        val status = StringBuilder()
        if (!engine.isReady(status))
            throw RuntimeException("[engine error] engine is not ready:n$status")

        distance = engine.getInputVariable("dist")
        headingDiff = engine.getInputVariable("hDiff")
        speedDiff = engine.getInputVariable("sDiff")

        headingChange = engine.getOutputVariable("hChg")
        speedChange = engine.getOutputVariable("sChg")
    }

    fun compute(distance: Int, headingDiff: Int, speedDiff: Int) =
        compute(distance.toDouble(), headingDiff.toDouble(), speedDiff.toDouble())

    fun compute(distance: Double, headingDiff: Double, speedDiff: Double) {
        this.distance.value = distance
        this.headingDiff.value = headingDiff
        this.speedDiff.value = speedDiff
        compute()
    }

    fun compute() = engine.process()
}
