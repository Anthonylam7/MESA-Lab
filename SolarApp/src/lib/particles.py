from kivy.uix.widget import Widget
from kivy.graphics import RenderContext
from kivy.clock import Clock
from kivy.graphics import Rectangle, Mesh
from kivy.properties import StringProperty

from kivy.graphics.transformation import Matrix
from src.lib.gl_constants import particle_shader

from math import sin,cos
from random import random

NUM_PARTICLE = 10000

class EnergyParticle(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True)
        super().__init__(**kwargs)
        self.canvas.shader.fs = particle_shader
        self.start = [0.0, 300.0]
        self.loc = list(self.start)
        self.end = 800.0
        self.t = 0
        self.off = random()*100
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.t += dt
        self.loc[0] += 3.0 #300*sin(self.t-3.1415/2) + 400
        self.loc[1] = 300*sin(self.t) + 300
        if self.loc[0] > self.end:
            self.loc[0] = self.start[0]
        self.canvas["time"] = Clock.get_boottime() + self.off
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas["offsets"] = self.loc


class ParticleEngine(Widget):
    '''
    The particle engine class is a wrapper for render context and provides an easy entry point
    for add graphics to an app as well as allowing for easy of management of those contents.

    Usage:
    1. A user define a shader for the engine to use.
    2. Call the format_mesh method to configure the mesh
    3. Call the add_vertex method
    4. Optionally, users may call add_indices
    '''
    shader = StringProperty("")
    def __init__(self, **kwargs):
        self.canvas = RenderContext(use_parent_projection=True, use_parent_matview=True, compute_normal_mat=True)
        super(ParticleEngine, self).__init__(**kwargs)
        self._draw_loop = None
        self._format = None
        self._vertices = ()
        self._indices = ()

    def set_shader(self, fs, vs):
        shader = self.canvas.shader
        backup = shader.fs
        backup2 = shader.vs
        shader.fs = fs
        shader.vs = vs
        if not shader.success:
            self.canvas.shader.fs = backup
            shader.vs = backup2
            print(backup, shader.vs)
            raise Exception("Failed setting shader.")

    def format_mesh(self, format):
        '''
        set the format to apply to the mesh.
            sample_fmt = (
                (b'vCenter',     2, 'float'),
                (b'vPosition',   2, 'float'),
                (b'vTexCoords0', 2, 'float'),
            )
        :param format:
        :return:
        '''
        self._format = format

    def add_vertex(self, vertex):
        """
            based on sample format
            sample_vertices = (
                128, 128, -width//2, -height//2, u0, v1,
                128, 128,  width//2, -height//2, u1, v1,
                128, 128,  width//2,  height//2, u1, v0,
                128, 128, -width//2,  height//2, u0, v0,
            )
        :param vertex: tuple of format compliant indices
        :return:
        """
        if not self._vertices:
            self._vertices = vertex
        else:
            self._vertices += vertex

    def add_indices(self, indices):
        if not self._indices:
            self._indices = indices
        else:
            self._indices += indices

    def update(self, dt):
        self.canvas["time"] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas["offsets"] = (400.0, 300.0)
        # asp = self.width / float(self.height)
        # proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        # self.canvas['projection_mat'] = proj
        with self.canvas:
            self.canvas.clear()
            Mesh(
                fmt=self._format,
                indices=self._indices,
                vertices=self._vertices,
                mode="triangles"
            )

    def draw(self):
        self._draw_loop = Clock.schedule_interval(self.update, 1/60)

    def stop(self):
        self._draw_loop.stop()

class ParticleManager(ParticleEngine):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._particles = []
        self._curIndex = 0
        self._formatLength = 0

    def format_mesh(self, format):
        super().format_mesh(format)
        self._formatLength = sum([row[1] for row in format])

    def addParticle(self, obj):
        """
        add particles to the Manager and keeps track of the particle index.
        :param obj:
        :return:
        """
        obj.attach(self, self._curIndex)
        obj._formatLength = self._formatLength
        self._particles.append(obj)
        self.add_vertex(obj.vertices)
        idx = len(self._particles)-1
        indices = [idx*4 + i for i in range(3)]
        indices.extend([idx*4 + 2, idx*4+3, idx*4])
        self.add_indices(indices)
        self._curIndex += self._formatLength*4

    def update(self, dt):
        for particle in self._particles:
            particle.update(dt)
        super().update(dt)


class Particle:
    """
    Each particle is responsible for updating its own vertex
    This is achieved by attaching itself to the managing class
    The managing class will call the particle instance "update" method  every frame
    """
    def __init__(self, **kwargs):
        super().__init__()
        self._index = None
        self._manager = None
        self._formatLength = None
        self.vertices = []


    def set_vertices(self, vertices):
        self.vertices = vertices

    def attach(self, manager, index):
        self._manager = manager
        self._index = index

    def update(self, dt):
        raise NotImplementedError(str(type(self)) + " does not have an update method")




if __name__ == "__main__":
    from kivy.app import App
    from kivy.core.window import EventLoop
    from src.lib.gl_constants import test_fragment_shader, test_vertex_shader, ENERGY_FRAGMENT_SHADER, ENERGY_VERTEX_SHADER
    class ParticlesApp(App):
        def build(self):
            EventLoop.ensure_window()
            p = ParticleManager()
            p.set_shader(fs=ENERGY_FRAGMENT_SHADER, vs=ENERGY_VERTEX_SHADER)
            p.format_mesh(
                format=
                (
                    (b'vPosition', 2, "float"),
                    (b"vTexture0", 2, "float"),
                    (b"vCenter", 2, "float")
                )
            )
            vertices = []
            indices = []
            import random
            for i in range(0, 4*NUM_PARTICLE, 4):
                # x = random.random()*800
                # y = random.random()*600
                x =  200*(0.5*random.random()+0.7)*sin(i-3.14159/2) + 400
                y = 200* (0.5*random.random()+0.7)* sin(i) + 300
                vertices.extend([x - 100., y-100., 0.0, 0.0, x, y])
                vertices.extend([x - 100., y + 100., 0.0, 0.0, x, y])
                vertices.extend([x + 100., y + 100., 0.0, 0.0, x, y])
                vertices.extend([x + 100., y - 100., 0.0, 0.0, x, y])
                indices.extend([i, i+1, i+2, i+2, i+3, i])
            #vertices = tuple(vertices)
            indices = tuple(indices)
            p.add_vertex(vertices)
            p.add_indices(indices)



            # p.add_vertex((
            #     400.0, 300.0, 0.0, 0.0, 500.0, 400.0,
            #     400.0, 500.0, 0.0, 1.0, 500.0, 400.0,
            #     600.0, 500.0, 1.0, 1.0, 500.0, 400.0,
            #     600.0, 300.0, 1.0, 0.0, 500.0, 400.0,
            #
            #     200.0, 300.0, 0.0, 0.0, 300.0, 400.0,
            #     200.0, 500.0, 0.0, 1.0, 300.0, 400.0,
            #     400.0, 500.0, 1.0, 1.0, 300.0, 400.0,
            #     400.0, 300.0, 1.0, 0.0, 300.0, 400.0
            # ))
            # p.add_indices((0, 1, 2,
            #                2, 3, 0,
            #
            #                4, 5, 6,
            #                6, 7, 4,
            #                ))
            p.draw()
            return p


    ParticlesApp().run()