package com.boids

object Settings {

    const val VANILLA = true
    const val SEEDED_RANDOM = true

    const val FLOCK_SIZE = 50

    const val MAX_FORCE = 1f
    const val MAX_SPEED = 2f

    const val ALIGNMENT_WEIGHT = 0.3f
    const val COHESION_WEIGHT = 1.2f
    const val SEPARATION_WEIGHT = 1.25f

    const val PERCEPTION_RADIUS = 80f // alignmentRadius and cohesionRadius
    const val SEPARATION_RADIUS = 30f

    const val SHOW_PERCEPTION_RADIUS = false
    const val SHOW_SEPARATION_RADIUS = false
    const val SHOW_FORCES = false

    const val METRICS_CHARTING_RATE = 300
}