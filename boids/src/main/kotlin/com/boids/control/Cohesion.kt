package com.boids.control

import com.boids.Sketch.Companion.vanilla
import net.sourceforge.jFuzzyLogic.FIS
import net.sourceforge.jFuzzyLogic.plot.JFuzzyChart
import net.sourceforge.jFuzzyLogic.rule.Variable
import java.io.File
import java.nio.file.Paths

object Cohesion {
    private val fclFileName =
        if (vanilla) Paths.get(".", "src", "fcl", "vanilla", "cohere.fcl").toString()
        else Paths.get(".", "src", "fcl", "cohere.fcl").toString()
    private val fis = FIS.load(fclFileName, true)

    val distance: Variable = fis.getVariable("distance") // input
    val position: Variable = fis.getVariable("position") // input
    val headingChange: Variable = fis.getVariable("headingChange") // output

    private val chart = JFuzzyChart.get()

    init {
        if (fis == null) throw RuntimeException("[FIS error] couldn't load file")
        if (chart == null) throw RuntimeException("[JFuzzyChart error] couldn't get JFuzzyChart")
    }

    fun evaluate(distance: Float, position: Float) = evaluate(distance.toDouble(), position.toDouble())

    fun evaluate(distance: Double, position: Double) {
        this.distance.value = distance
        this.position.value = position
        evaluate()
    }

    fun evaluate() = fis.evaluate()

    // Show variable's membership functions
    fun showFIS() {
        chart.chart(fis)
    }

    // Show output variable's chart
    fun showOutput() {
        chart.chart(headingChange, headingChange.defuzzifier, true) // show defuzzifier
        chart.chart(headingChange, true) // show each linguistic term
    }

    // Show each rule (and degree of support)
    fun printRules() = fis
        .getFunctionBlock("cohesion")
        .getFuzzyRuleBlock("cohesion")
        .rules.forEach { println(it) }
}

fun main() {
    //Cohesion.showFIS()
    val bool = false

    // bool == true: test individual inputs and see their charts
    while (bool) {
        val inp = readLine()!!.split(',')
        Cohesion.evaluate(distance = inp[0].toDouble(), position = inp[1].toDouble())

        Cohesion.printRules()
        Cohesion.showOutput()

        println("Antecedent: distance ${Cohesion.distance.value}, position ${Cohesion.position.value}")
        println("Consequent: headingChange ${Cohesion.headingChange.value}")
    }

    // bool == false
    val deltaDist = 10
    val deltaPos = 36
    val csvFile = File(Paths.get(".", "metrics", "heatmap", "cohesion_cog.csv").toString())
    csvFile.writeText("distance,position,headingChange\n")
    for (dist in 0..100 step deltaDist) {
        println("finished line $dist")
        for (pos in -180..180 step deltaPos) {
            Cohesion.evaluate(distance = dist / 1.0, position = pos / 1.0)
            csvFile.appendText("$dist,$pos,${Cohesion.headingChange.value}\n")
        }
    }
}