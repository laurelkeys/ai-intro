package com.boids

import net.sourceforge.jFuzzyLogic.FIS
import net.sourceforge.jFuzzyLogic.plot.JFuzzyChart
import java.nio.file.Paths


/**
 * Test parsing an FCL file
 * @author pcingola@users.sourceforge.net
 */
object TestTipper {
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
        // Load from 'FCL' file
        val fileName = Paths.get(".", "src", "fcl", "cohere.fcl").toAbsolutePath().toString()
        val fis = FIS.load(fileName, true)

        // Error while loading?
        if (fis == null) {
            System.err.println("Can't load file: '$fileName'")
            return
        }
        val dist = fis.getVariable("dist")
        val pDiff = fis.getVariable("pDiff")
        val hChg = fis.getVariable("hChg")

        // Show
        JFuzzyChart.get().chart(fis)

        // Set inputs
        while (true) {
            val inp = readLine()!!.split(',')
            dist.value = inp[0].toDouble()
            pDiff.value = inp[1].toDouble()

            // Evaluate
            fis.evaluate()

            // Show output variable's chart
            JFuzzyChart.get().chart(hChg, hChg.defuzzifier, true)

            // Show each rule (and degree of support)
            fis
                .getFunctionBlock("cohesion")
                .getFuzzyRuleBlock("cohesion")
                .rules.forEach { println(it) }

            println("Antecedent: dist ${dist.value}, pDiff ${pDiff.value}")
            println("Consequent: hChg ${hChg.value}")
        }
    }
}