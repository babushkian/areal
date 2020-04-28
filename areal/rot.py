from areal import constants as cn
from areal.proto import Plant_proto

class Rot(Plant_proto):
    COUNT = 0
    # скорость гнеиния
    DECAY_SPEED = cn.PLANT_MAX_MASS / cn.MONTHS * cn.DECAY_MULTIPLIER
    def __init__(self, field, sx ,sy, all_energy):
        self.name = 'rot'
        super().__init__(field, sx, sy)
        self.world = field.world
        self.field = field
        self.all_energy = all_energy
        self.state = 0
        self.field.rot[self.id] = self
        # self.world.tag_lower(self.id)
        # self.world.tag_raise('rot')

    # гниль медленно превращается в землю - на каждом ходу образуется немного земли
    def update_continuous(self):
        super().update()
        decrement = min(self.all_energy, self.DECAY_SPEED)
        self.all_energy -= decrement
        self.field.soil += decrement
        if self.all_energy == 0:
            self.become_soil()

    # гниль долго гниет, а потом разом превращается в почву
    def update(self):
        super().update()
        self.state += self.DECAY_SPEED
        if self.all_energy - self.state < self.DECAY_SPEED :
            self.become_soil()


    def become_soil(self):
        self.del_img()
        self.count_down()
        self.field.soil += self.all_energy  # растение превращается в почву
        del self.field.rot[self.id]

