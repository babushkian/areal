from areal import constants as cn
from areal.proto import Plant_proto

class Rot(Plant_proto):
    # скорость гнеиния
    DECAY_SPEED = cn.PLANT_MAX_MASS / cn.MONTHS * cn.DECAY_MULTIPLIER
    def __init__(self, field, app, sx ,sy, mass):
        self.name = 'rot'
        super().__init__(field, app, sx, sy)
        self.world = field.world
        self.field = field
        self.mass = mass
        self.state = 0
        self.world.rot[self.id] = self
        self.field.rot[self.id] = self
        # self.world.tag_lower(self.id)
        # self.world.tag_raise('rot')

    # гниль медленно превращается в землю - на каждом ходу образуется немного земли
    def update_continuous(self):
        decrement = min(self.mass, self.DECAY_SPEED)
        self.mass -= decrement
        self.field.soil += decrement
        if self.mass == 0:
            self.become_soil()

    # гниль долго гниет, а потом разом превращается в почву
    def update(self):
        self.state += self.DECAY_SPEED
        if self.mass - self.state < self.DECAY_SPEED :
            self.become_soil()


    def become_soil(self):
        self.del_img()
        self.field.soil += self.mass  # растение превращается в почву
        del self.world.rot[self.id]
        del self.field.rot[self.id]
