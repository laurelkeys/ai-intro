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
        val fileName = Paths.get(".", "src", "fcl", "align.fcl").toAbsolutePath().toString()
        val fis = FIS.load(fileName, true)

        // Error while loading?
        if (fis == null) {
            System.err.println("Can't load file: '$fileName'")
            return
        }

        // Show
        JFuzzyChart.get().chart(fis)

        // Set inputs
        fis!!.setVariable("service", 3.0)
        fis!!.setVariable("food", 7.0)

        // Evaluate
        fis!!.evaluate()

        // Show output variable's chart
        val tip = fis.getVariable("tip")
        JFuzzyChart.get().chart(tip, tip.getDefuzzifier(), true)

        // Print ruleSet
        System.out.println(fis)
    }
}