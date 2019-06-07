package com.boids.extensions

import processing.core.PVector

fun PVector.add(vararg vectors: PVector): PVector {
    vectors.forEach { this.add(it) }
    return this
}