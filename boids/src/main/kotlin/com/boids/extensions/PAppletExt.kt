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

operator fun Number.times(vector: PVector): PVector = PVector.mult(vector, this.toFloat())

fun PApplet.lineTo(position: PVector) {
    this.line(0f, 0f, position.x, position.y) // draws a line from the origin
}

fun PApplet.circle(x: Number = 0f, y: Number = 0f, radius: Number) {
    this.ellipse(x.toFloat(), y.toFloat(), radius.toFloat(), radius.toFloat())
}