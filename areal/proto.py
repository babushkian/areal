from areal import constants as cn
class Plant_proto:

    def __init__(self, field, sx, sy, draw = True):
        self.world = field.world
        self.field = field
        self.name = None
        # координаты экранного пространства,  а не физические
        self.sx = sx
        self.sy = sy
        self.draw = draw
        self.age = 0
        #self.id = self.world.create_rectangle(self.sx - 3, self.sy - 3, self.sx + 3, self.sy + 3, fill=self.color)

    def create_img(self, size, color, border):
        if self.draw:
            self.id = self.world.create_rectangle(self.sx - size, self.sy - size, self.sx + size, self.sy + size, fill=color, width=border, tags =self.name)
        else:
            self.id = cn.global_counter()

    def del_img(self):
        if self.draw:
            self.world.delete(self.id)
