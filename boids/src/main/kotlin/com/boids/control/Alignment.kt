package com.boids.control

import net.sourceforge.jFuzzyLogic.FIS
import net.sourceforge.jFuzzyLogic.plot.JFuzzyChart
import net.sourceforge.jFuzzyLogic.rule.Variable
import java.nio.file.Paths

object Alignment {
    private val fclFileName = Paths.get(".", "src", "fcl", "vanilla", "align.fcl").toString()
    private val fis = FIS.load(fclFileName, true)

    val distance: Variable = fis.getVariable("distance") // input
    val direction: Variable = fis.getVariable("direction") // input
    val headingChange: Variable = fis.getVariable("headingChange") // output

    private val chart = JFuzzyChart.get()

    init {
        if (fis == null) throw RuntimeException("[FIS error] couldn't load file")
        if (chart == null) throw RuntimeException("[JFuzzyChart error] couldn't get JFuzzyChart")
    }

    fun evaluate(distance: Float, direction: Float) = evaluate(distance.toDouble(), direction.toDouble())

    fun evaluate(distance: Double, direction: Double) {
        this.distance.value = distance
        this.direction.value = direction
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
        .getFunctionBlock("alignment")
        .getFuzzyRuleBlock("alignment")
        .rules.forEach { println(it) }
}

fun main() {
    Alignment.showFIS()
    val bool = false

    // bool == true: test individual inputs and see their charts
    while (bool) {
        val inp = readLine()!!.split(',')
        Alignment.evaluate(distance = inp[0].toDouble(), direction = inp[1].toDouble())

        Alignment.printRules()
        Alignment.showOutput()

        println("Antecedent: distance ${Alignment.distance.value}, direction ${Alignment.direction.value}")
        println("Consequent: headingChange ${Alignment.headingChange.value}")
    }

    // bool == false: test pDiff values from -180 to 180
    for (i in -180..180 step 10) {
        Alignment.evaluate(distance = 60.0, direction = i / 1.0)
        println("$i -> ${Alignment.headingChange.value}")
    }
}