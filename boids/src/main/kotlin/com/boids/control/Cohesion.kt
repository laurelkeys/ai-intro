package com.boids.control

import net.sourceforge.jFuzzyLogic.FIS
import net.sourceforge.jFuzzyLogic.plot.JFuzzyChart
import net.sourceforge.jFuzzyLogic.rule.Variable
import java.lang.RuntimeException
import java.nio.file.Paths

object Cohesion {
    private val fclFileName = Paths.get(".", "src", "fcl", "cohere.fcl").toString()
    private val fis = FIS.load(fclFileName, true)

    val distance: Variable = fis.getVariable("dist") // input
    val positionDiff: Variable = fis.getVariable("pDiff") // input
    val headingChange: Variable = fis.getVariable("hChg") // output

    private val chart = JFuzzyChart.get()

    init {
        if (fis == null) throw RuntimeException("[FIS error] couldn't load file")
        if (chart == null) throw RuntimeException("[JFuzzyChart error] couldn't get JFuzzyChart")
    }

    fun evaluate(distance: Double, positionDiff: Double) {
        this.distance.value = distance
        this.positionDiff.value = positionDiff
        evaluate()
    }

    fun evaluate() = fis.evaluate()

    // Show variable's membership functions
    fun showFIS() {
        chart.chart(fis)
    }

    // Show output variable's chart
    fun showOutput() {
        //chart.chart(headingChange, headingChange.defuzzifier, true) // show defuzzifier
        chart.chart(headingChange, true) // show each linguistic term
    }

    // Show each rule (and degree of support)
    fun printRules() {
        fis
            .getFunctionBlock("cohesion")
            .getFuzzyRuleBlock("cohesion")
            .rules.forEach { println(it) }
    }
}

fun main() {
    Cohesion.showFIS()
    while (true) {
        val inp = readLine()!!.split(',')
        Cohesion.evaluate(distance = inp[0].toDouble(), positionDiff = inp[1].toDouble())

        Cohesion.printRules()
        Cohesion.showOutput()

        println("Antecedent: dist ${Cohesion.distance.value}, pDiff ${Cohesion.positionDiff.value}")
        println("Consequent: hChg ${Cohesion.headingChange.value}")
    }
}