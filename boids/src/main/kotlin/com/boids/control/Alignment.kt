package com.boids.control

import net.sourceforge.jFuzzyLogic.FIS
import net.sourceforge.jFuzzyLogic.plot.JFuzzyChart
import net.sourceforge.jFuzzyLogic.rule.Variable
import java.io.File
import java.nio.file.Paths

object Alignment {
    private val fclFileName = Paths.get(".", "src", "fcl", "vanilla", "align.fcl").toString()
    private val fis = FIS.load(fclFileName, true)

    val direction: Variable = fis.getVariable("direction") // input
    val headingChange: Variable = fis.getVariable("headingChange") // output

    private val chart = JFuzzyChart.get()

    init {
        if (fis == null) throw RuntimeException("[FIS error] couldn't load file")
        if (chart == null) throw RuntimeException("[JFuzzyChart error] couldn't get JFuzzyChart")
    }

    fun evaluate(direction: Float) = evaluate(direction.toDouble())

    fun evaluate(direction: Double) {
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
        Alignment.evaluate(direction = inp[0].toDouble())

        Alignment.printRules()
        Alignment.showOutput()

        println("Antecedent: direction ${Alignment.direction.value}")
        println("Consequent: headingChange ${Alignment.headingChange.value}")
    }

    // bool == false
    val deltaDir = 36
    val csvFile = File(Paths.get(".", "metrics", "heatmap", "alignment-$deltaDir.csv").toString())
    csvFile.writeText("direction,headingChange\n")
    for (dir in -180..180 step deltaDir) {
        Alignment.evaluate(direction = dir / 1.0)
        csvFile.appendText("$dir,${Alignment.headingChange.value}\n")
    }
}