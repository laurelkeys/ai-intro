package com.boids

const val VANILLA = true
const val SEED_RANDOM = true

const val FLOCK_SIZE = 50

const val BOID_SIZE_SCALE = 2f // boid size drawing scaling
const val BOID_FORCE_SCALE = 40f // steering force vector drawing scaling

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
const val SHOW_FPS = true

const val PLOTTING = true
const val METRICS_CHARTING_RATE = 1000