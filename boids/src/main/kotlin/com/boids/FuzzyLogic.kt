package com.boids

import com.fuzzylite.Op
import com.fuzzylite.FuzzyLite
import com.fuzzylite.imex.FclImporter
import java.io.File
import java.io.File.separatorChar

object FuzzyLogic {
    @JvmStatic
    fun main(args: Array<String>) {
        val engine = FclImporter().fromFile(
            File(".${separatorChar}src${separatorChar}fcl${separatorChar}alignment.fcl")
        )

        val status = StringBuilder()
        if (!engine.isReady(status))
            throw RuntimeException("[engine error] engine is not ready:n$status")

        val distance = engine.getInputVariable("dist")
        val headingDiff = engine.getInputVariable("hDiff")
        val speedDiff = engine.getInputVariable("sDiff")

        val headingChange = engine.getOutputVariable("hChg")
        val speedChange = engine.getOutputVariable("sChg")

        distance.value = 0.0
        headingDiff.value = 0.0
        speedDiff.value = 0.0

        engine.process()

        FuzzyLite.logger().info(
            String.format(
                "distance.input = %s, headingDiff.input = %s, speedDiff.input = %s -> headingChange.output = %s, speedChange.output = %s",
                Op.str(distance.value), Op.str(headingDiff.value), Op.str(speedDiff.value), Op.str(headingChange.value), Op.str(speedChange.value)
            )
        )
    }
}