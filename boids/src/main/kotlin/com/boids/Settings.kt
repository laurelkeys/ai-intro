package com.boids

const val SEED_RANDOM = false

const val VANILLA = true
const val THINK_FUZZY = false

const val FLOCK_SIZE = 50

const val BOID_SIZE_SCALE = 3f // boid size drawing scaling
const val BOID_FORCE_SCALE = 40f // steering force vector drawing scaling

const val MAX_FORCE = 1f
const val MAX_SPEED = 2f

const val ALIGNMENT_WEIGHT = 0.3f
const val COHESION_WEIGHT = 1.2f
const val SEPARATION_WEIGHT = 1.4f

const val PERCEPTION_RADIUS = 80f // alignmentRadius and cohesionRadius
const val SEPARATION_RADIUS = 30f

const val SHOW_PERCEPTION_RADIUS = false
const val SHOW_SEPARATION_RADIUS = false
const val SHOW_FORCES = false
const val SHOW_FPS = false

const val PLOTTING = false
const val METRICS_CHARTING_RATE = 1000