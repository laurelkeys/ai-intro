package com.boids

import com.fuzzylite.Engine
import com.fuzzylite.Op
import com.fuzzylite.FuzzyLite
import com.fuzzylite.imex.FclImporter
import com.fuzzylite.variable.InputVariable
import com.fuzzylite.variable.OutputVariable
import java.io.File
import java.io.File.separatorChar

object FuzzyLogic {
    private val engine = FclImporter().fromFile(
        File(".${separatorChar}src${separatorChar}fcl${separatorChar}alignment.fcl")
    )!!

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

    fun compute(distance: Double, headingDiff: Double, speedDiff: Double) {
        this.distance.value = distance
        this.headingDiff.value = headingDiff
        this.speedDiff.value = speedDiff
        compute()
    }

    fun compute() {
        engine.process()
        FuzzyLite.logger().info(
            String.format(
                "distance.input = %s, headingDiff.input = %s, speedDiff.input = %s -> headingChange.output = %s, speedChange.output = %s",
                Op.str(distance.value),
                Op.str(headingDiff.value),
                Op.str(speedDiff.value),
                Op.str(headingChange.value),
                Op.str(speedChange.value)
            )
        )
    }

    @JvmStatic
    fun main(args: Array<String>) {


        distance.value = 0.0
        headingDiff.value = 0.0
        speedDiff.value = 0.0

        engine.process()


    }
}


fun main(args: Array<String>) {
    FuzzyLogic.distance.value = 0.0
    FuzzyLogic.headingDiff.value = 0.0
    FuzzyLogic.speedDiff.value = 0.0

    FuzzyLogic.process()
}