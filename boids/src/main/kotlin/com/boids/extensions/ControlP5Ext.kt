package com.boids.extensions

import controlP5.ControlP5
import controlP5.ControlP5Constants.ACTION_BROADCAST
import controlP5.Slider
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
        if (it.action == ACTION_BROADCAST) {
            onValueChange(it.controller.value)
        }
    }

fun ControlP5.addSlider(
    name: String,
    max: Number,
    min: Number = 0,
    default: Number,
    position: Pair<Number, Number>,
    onValueChange: (Float) -> Unit
): Slider = this
    .addSlider(
        name,
        min.toFloat(),
        max.toFloat(),
        default.toFloat(),
        position.first.toInt(),
        position.second.toInt(),
        100,
        10
    )
    .addCallback {
        if (it.action == ACTION_BROADCAST) {
            onValueChange(it.controller.value)
        }
    }