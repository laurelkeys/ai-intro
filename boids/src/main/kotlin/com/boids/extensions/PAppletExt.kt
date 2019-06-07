package com.boids.extensions

import processing.core.PApplet
import processing.core.PVector


fun PApplet.pushPop(origin: PVector, angle: Float = 0f, transformation: () -> Unit) {
    pushPop(origin.x, origin.y, angle, transformation)
}

fun PApplet.pushPop(x: Float = 0f, y: Float = 0f, angle: Float = 0f, transformation: () -> Unit) {
    pushMatrix() // saves the current coordinate system to the stack
    translate(x, y)
    rotate(angle)

    transformation()

    popMatrix() // restores the prior coordinate system
}

fun PApplet.random(high: Number): Float = this.random(high.toFloat())