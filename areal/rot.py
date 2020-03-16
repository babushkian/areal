from . import world as wd
from . import plant


class Rot:
    # крупное растение разлагается за год
    DECAY_SPEED = 1 # неверная установка, значение инициализируется ниже
    DECAY_MULTIPLIER = 0.3 # скорость гниения, гем больше, тем быстрее
    def __init__(self, field, sx ,sy, mass = plant.SEED_MASS+plant.START_CONSUMED, color = wd.ROT_COLOR):
        self.world = field.world
        self.canvas = field.world.canvas
        self.field = field
        self.mass = mass
        self.state = 0
        self.color =  color #'saddle brown' 'purple4'''dark goldenrod'
        self.id = self.canvas.create_rectangle(sx-2, sy-2,
                                               sx+2, sy+2, width=0,
                                               fill=self.color)
        self.world.rot[self.id] = self
        self.field.rot[self.id] = self
        # self.canvas.tag_lower(self.id)
        # self.canvas.tag_raise('rot')

    @staticmethod
    def init_constants():
        Rot.DECAY_SPEED = plant.MAX_MASS / wd.MONTS * Rot.DECAY_MULTIPLIER

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
        self.canvas.delete(self.id)
        self.field.soil += self.mass  # растение превращается в почву
        del self.world.rot[self.id]
        del self.field.rot[self.id]
