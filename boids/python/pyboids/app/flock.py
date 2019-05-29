"""Flock class."""
import pygame
import numpy as np
from . import params, utils
from .boid import Boid, LeaderBoid
from .obstacle import Obstacle


class Flock(pygame.sprite.Sprite):
    """Represents a set of boids that obey to certain behaviours."""

    def __init__(self):
        super().__init__()
        self.normal_boids = pygame.sprite.Group()
        self.leader_boid = pygame.sprite.GroupSingle()
        self.boids = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.behaviours = {
            'pursue': False,
            'escape': False,
            'wander': True,
            'avoid collision': True,
            'follow leader': False,
            'align': False,
            'separate': False,
        }
        self.kinds = ['normal-boid', 'leader-boid', 'obstacle']
        self.add_kind = 'normal-boid'

    def switch_element(self):
        self.kinds = np.roll(self.kinds, -1)
        self.add_kind = self.kinds[0]

    def add_element(self, pos):
        """Add a boid at pos.

        The type of boid is the current add_kind value.
        """
        angle = np.pi * (2 * np.random.rand() - 1)
        vel = params.BOID_MAX_SPEED * np.array([np.cos(angle), np.sin(angle)])
        if self.add_kind == 'normal-boid':
            self.normal_boids.add(Boid(pos=np.array(pos), vel=vel))
            self.boids.add(self.normal_boids)
        elif self.add_kind == 'leader-boid':
            self.boids.remove(self.leader_boid)
            self.leader_boid.add(LeaderBoid(pos=np.array(pos), vel=vel))
            self.boids.add(self.leader_boid)
        elif self.add_kind == 'obstacle':
            self.obstacles.add(Obstacle(pos=pos))

    def remain_in_screen(self):
        for boid in self.boids:
            if boid.pos[0] > params.SCREEN_WIDTH - params.BOX_MARGIN:
                boid.steer(np.array([-params.STEER_INSIDE, 0.]))
            if boid.pos[0] < params.BOX_MARGIN:
                boid.steer(np.array([params.STEER_INSIDE, 0.]))
            if boid.pos[1] < params.BOX_MARGIN:
                boid.steer(np.array([0., params.STEER_INSIDE]))
            if boid.pos[1] > params.SCREEN_HEIGHT - params.BOX_MARGIN:
                boid.steer(np.array([0., -params.STEER_INSIDE]))

    def seek_single(self, target_pos, boid):
        d = utils.dist(boid.pos, target_pos)
        steering = (
            utils.normalize(target_pos - boid.pos) *
            params.BOID_MAX_SPEED * min(d / params.R_SEEK, 1) -
            boid.vel)
        boid.steer(steering, alt_max=params.BOID_MAX_FORCE / 50)

    def seek(self, target_boid):
        """Make all normal boids seek to go to a target."""
        for boid in self.normal_boids:
            self.seek_single(target_boid, boid)

    def flee_single(self, target_pos, boid):
        too_close = utils.dist2(boid.pos, target_pos) < params.R_FLEE**2
        if too_close:
            steering = (utils.normalize(boid.pos - target_pos) *
                        params.BOID_MAX_SPEED -
                        boid.vel)
            boid.steer(steering, alt_max=params.BOID_MAX_FORCE / 10)

    def flee(self, target_boid):
        """Make all normal boids fly away from a target."""
        for boid in self.normal_boids:
            self.flee_single(target_boid, boid)

    def pursue_single(self, target_pos, target_vel, boid):
        t = int(utils.norm(target_pos - boid.pos) / params.BOID_MAX_SPEED)
        future_pos = target_pos + t * target_vel
        self.seek_single(future_pos, boid)

    def pursue(self, target_boid):
        """Make all normal boids pursue a target boid with anticipation."""
        for boid in self.normal_boids:
            self.pursue_single(target_boid.pos, target_boid.vel, boid)

    def escape_single(self, target_pos, target_vel, boid):
        t = int(utils.norm(target_pos - boid.pos) / params.BOID_MAX_SPEED)
        future_pos = target_pos + t * target_vel
        self.flee_single(future_pos, boid)

    def escape(self, target_boid):
        """Make all normal boids escape a target boid with anticipation."""
        for boid in self.normal_boids:
            self.escape_single(target_boid.pos, target_boid.vel, boid)

    def wander(self):
        """Make all boids wander around randomly."""
        rands = 2 * np.random.rand(len(self.boids)) - 1
        cos = np.cos([b.wandering_angle for b in self.boids])
        sin = np.sin([b.wandering_angle for b in self.boids])
        for i, boid in enumerate(self.boids):
            nvel = utils.normalize(boid.vel)
            # calculate circle center
            circle_center = nvel * params.WANDER_DIST
            # calculate displacement force
            c, s = cos[i], sin[i]
            displacement = np.dot(
                np.array([[c, -s], [s, c]]), nvel * params.WANDER_RADIUS)
            boid.steer(circle_center + displacement)
            boid.wandering_angle += params.WANDER_ANGLE * rands[i]

    def find_most_threatening_obstacle(self, boid, aheads):
        most_threatening = None
        distance_to_most_threatening = float('inf')
        for obstacle in self.obstacles:
            norms = [utils.norm2(obstacle.pos - ahead) for ahead in aheads]
            if all(n > obstacle.radius * obstacle.radius for n in norms):
                continue
            distance_to_obstacle = utils.dist2(boid.pos, obstacle.pos)
            if most_threatening is not None and \
                    distance_to_obstacle > distance_to_most_threatening:
                continue
            most_threatening = obstacle
            distance_to_most_threatening = utils.dist2(boid.pos,
                                                       most_threatening.pos)
        return most_threatening

    def avoid_collision(self):
        """Avoid collisions between boids and obstacles."""
        for boid in self.boids:
            ahead = boid.pos + boid.vel / params.BOID_MAX_SPEED * \
                params.MAX_SEE_AHEAD
            ahead2 = boid.pos + boid.vel / params.BOID_MAX_SPEED / 2 * \
                params.MAX_SEE_AHEAD
            most_threatening = self.find_most_threatening_obstacle(
                boid, [ahead, ahead2, boid.pos])
            if most_threatening is not None:
                steering = utils.normalize(ahead - most_threatening.pos)
                steering *= params.MAX_AVOID_FORCE
                boid.steer(steering)

    def separate_single(self, boid):
        number_of_neighbors = 0
        force = np.zeros(2)
        for other_boid in self.boids:
            if boid == other_boid:
                continue
            elif pygame.sprite.collide_rect(boid, other_boid):
                force -= other_boid.pos - boid.pos
                number_of_neighbors += 1
        if number_of_neighbors:
            force /= number_of_neighbors
        boid.steer(utils.normalize(force) * params.MAX_SEPARATION_FORCE)

    def separate(self):
        for boid in self.boids:
            self.separate_single(boid)

    def follow_leader(self, leader):
        """Make all normal boids follow a leader.

        Boids stay at a certain distance from the leader.
        They move away when in the leader's path.
        They avoid cluttering when behind the leader.
        """
        nvel = utils.normalize(leader.vel)
        behind = leader.pos - nvel * params.LEADER_BEHIND_DIST
        ahead = leader.pos + nvel * params.LEADER_AHEAD_DIST
        for boid in self.normal_boids:
            self.seek_single(behind, boid)
            self.escape_single(ahead, leader.vel, boid)

    def align(self):
        """Make all boids to align their velocities."""
        r2 = params.ALIGN_RADIUS * params.ALIGN_RADIUS
        # find the neighbors
        boids = list(self.normal_boids)
        neighbors = [[] for boid in boids]
        for i, boid in enumerate(boids):
            for j, other_boid in enumerate(boids):
                if j in neighbors[i]:
                    continue
                elif boid == other_boid:
                    continue
                elif utils.dist2(boid.pos, other_boid.pos) < r2:
                    neighbors[i].append(j)
                    neighbors[j].append(i)
        for i, boid in enumerate(boids):
            number_of_neighbors = len(neighbors[i])
            if number_of_neighbors:
                desired = np.zeros(2)
                for j in neighbors[i]:
                    desired += boids[j].vel
                boid.steer(desired / number_of_neighbors - boid.vel)

    def flock(self):
        """Simulate flocking behaviour : alignment + separation + cohesion."""
        self.align()
        for boid in self.boids:
            self.separate_single(boid)

    def update(self, motion_event, click_event):
        # apply steering behaviours
        if self.leader_boid:
            target = self.leader_boid.sprite
            self.behaviours['pursue'] and self.pursue(target)
            self.behaviours['escape'] and self.escape(target)
            self.behaviours['follow leader'] and self.follow_leader(target)
        self.behaviours['wander'] and self.wander()
        if self.behaviours['avoid collision'] and self.obstacles:
            self.avoid_collision()
        self.behaviours['align'] and self.align()
        self.behaviours['separate'] and self.separate()
        self.remain_in_screen()
        # update all boids
        for boid in self.boids:
            boid.update()

    def display(self, screen):
        for obstacle in self.obstacles:
            obstacle.display(screen)
        for boid in self.boids:
            boid.display(screen, debug=params.DEBUG)
        for boid in self.boids:
            boid.reset_frame()
