package com.boids.extensions

import controlP5.ControlP5
import controlP5.ControlP5Constants
import controlP5.Toggle

fun ControlP5.addToggle(
    name: String,
    label: String,
    value: Boolean,
    position: Pair<Number, Number>,
    onValueChange: (Float) -> Unit
): Toggle = this
    .addToggle(name)
    .setLabel(label)
    .setPosition(position.first.toFloat(), position.second.toFloat())
    .setSize(40, 10)
    .setValue(value)
    .setMode(ControlP5.SWITCH)
    .addCallback {
        if (it.action == ControlP5Constants.ACTION_BROADCAST) {
            onValueChange(it.controller.value)
        }
    }