from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup

class HelpPopUp(Popup):
    def __init__(self, title, content, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = ScrollView()
        self.content.add_widget(content)
        self.size_hint = (0.7, 0.8)


class HelpButton(Button):
    def __init__(self, title, content, **kwargs):
        super().__init__(**kwargs)
        self.popup = HelpPopUp(title, content)

    def on_release(self):
        self.popup.open()


class ScrollableDescription(ScrollView):
    """
    Container for displaying large text inside a scrollView
    """
    def __init__(self, desc="", **kwargs):
        super().__init__(**kwargs)
        self.text = Label(
            text=desc,
            size_hint_y = None,
            text_size = (self.width, None)
        )
        self.text.bind(texture_size=self.resize)
        self.add_widget(self.text)

    def resize(self, *args):
        self.text.text_size = (self.width, None)
        self.text.height = self.text.texture_size[1]

    def on_size(self, *args):
        self.resize()

    def changeText(self, text):
        self.text.text = text


class AttributeSlider(Slider):
    """
    Helper for tuning widget property via slider abstraction
    """
    def __init__(self, target, attribute, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.value = 50
        self.target = target
        self.targetAttribute = attribute
        self.bind(value=self.setAttribute)

    def setAttribute(self, *args):
        self.target.__setattr__(self.targetAttribute, self.value_normalized)


class ObjMesh:
    def __init__(self):
        self.indices = []
        self.vertices = []


class WavefrontObjReader:
    def __init__(self, pathToFile=None):
        if pathToFile == None:
            raise ValueError("Please supply a valid file path")
        self._vert = []
        self._text = []
        self._norm = []
        self._ind = []
        self._face = []
        self._object = {}

        self._path = pathToFile

        self.parseObjFile()

    def parseObjFile(self):
        curObj = None
        with open(self._path, "r") as objFile:
            for line in objFile.readlines():
                values = line.split()
                if len(values) == 0:
                    continue
                tag = values[0].lower()

                # Indicates start of an object
                if tag == "o":
                    if curObj is None:
                    # record the current file name
                        curObj = values[1]

                    else:
                        self.processObject(curObj)
                        self._face = []
                        curObj = values[1]

                # Read vertices
                elif tag == "v":
                    values = list(map(float, values[1:]))
                    self._vert.append(values)
                elif tag == "vn":
                    values = list(map(float, values[1:]))
                    self._norm.append(values)
                elif tag == "vt":
                    values = list(map(float, values[1:]))
                    self._text.append(values)
                elif tag == "f":
                    self._face.append(values[1:])
        if curObj is None:
            curObj = "default"
        self.processObject(curObj)
        print(self._object)

    def processObject(self, objectName):

        # construct vertex list
        vertices = []
        indices = []
        i = 0
        for face in self._face:
            for index in face:
                idx = [int(x) if x else 0 for x in index.split("/")]
                vertices.extend(self._vert[idx[0]-1])
                if idx[1]:
                    vertices.extend(self._text[idx[1]-1])
                else:
                    vertices.extend([0.0, 0.0])
                if idx[2]:
                    vertices.extend(self._norm[idx[2]-1])
                indices.append(i)
                i += 1
        m = ObjMesh()
        m.indices = indices
        m.vertices = vertices
        self._object[objectName] = m




if __name__ == "__main__":
    from kivy.app import App
    from kivy.core.window import EventLoop
    from src.lib.constants import PHOTOELECTRIC
    from src.lib.particles import ParticleEngine
    from src.lib.angleDep import Shape

    ANGLE_VS = """
    #ifdef GL_ES
        precision highp float;
    #endif

    /* Outputs to the fragment shader */
    varying vec3 norm;
    varying vec4 fragPos;

    /* vertex attributes */
    attribute vec3 vPosition;
    attribute vec2 vTexCoords0;
    attribute vec3 vNorm;

    /* uniform variables */
    uniform mat4       modelview_mat;
    uniform mat4       projection_mat;
    uniform float      time;
    void main(void)
    {
        float roll = 0., pitch=time, yaw=0.;
        
        mat4 translate = mat4(
                            60.0, 0.0, 0.0, 400.,
                            0.0, 60.0, 0.0, 100.,
                            0.0, 0.0, 1.0/800., -0., //-0.9+distance,
                            0.0, 0.0, 0.0, 1.0
                            );
        mat4 rotateX = mat4(
                            1.0, 0.0, 0.0, 0.0,
                            0.0, cos(roll), -sin(roll), 0.0,
                            0.0, sin(roll), cos(roll), 0.0,
                            0.0, 0.0, 0.0, 1.0
                            );
        mat4 rotateY = mat4(
                            cos(pitch), 0.0, sin(pitch), 0.0,
                            0.0, 1.0, 0.0, 0.0,
                            -sin(pitch), 0.0, cos(pitch), 0.0, 
                            0.0, 0.0, 0.0, 1.0
                            );
        mat4 rotateZ = mat4(
                            cos(yaw), -sin(yaw), 0.0, 0.0,
                            sin(yaw), cos(yaw), 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0
                            );
        vec4 pos = vec4(vPosition, 1.0) * rotateZ * rotateY * rotateX * translate;
        fragPos = modelview_mat * pos;
        vec4 temp = vec4(vNorm, 1.0) * rotateZ * rotateY * rotateX;
        norm = normalize(temp.xyz);
        gl_Position = projection_mat * modelview_mat *  pos ;
    }
    """

    ANGLE_FS = """
    #ifdef GL_ES
        precision highp float;
    #endif
    varying vec4 fragPos;
    varying vec3 norm;
    
    uniform float time;
    uniform mat4 normal_mat;
    void main(void)
    {
        vec4 light;
        vec4 temp = normalize( normal_mat * vec4(norm, 0.0) );
        float diffuse = 0.4;
        light = normalize(vec4(100. - 00., 400.-0., 0.+0., 0.) - fragPos);
        float directional = 1.0*max( dot(light.xyz, norm), 0.0);
        vec3 total =  diffuse * vec3(1.0, 1.0, 1.0) + directional * vec3(1.0, 1.0, 1.0);
        gl_FragColor = diffuse * vec4(1.,1.,1.,1.) *vec4(.5, 0.7, 0.9, 1.0) + 
                        directional*vec4(.9,.9,0.2,1.) *vec4(.0, 0.2, 0.5, 1.0) ; 
    }
    """


    class UtilsApp(App):
        def build(self):
            EventLoop.ensure_window()
            s = ScrollableDescription(desc=PHOTOELECTRIC)
            # hb = HelpButton("Help message", s, text="Press me!!!")
            p = ParticleEngine()
            p.set_shader(fs=ANGLE_FS, vs=ANGLE_VS)

            p.format_mesh(
                [
                    (b"vPosition", 3, "float"),
                    (b"vTexCoords0", 2, "float"),
                    (b"vNorm", 3, "float")
                 ]
            )

            w = WavefrontObjReader("../../assets/models/vehicleChassis.obj")
            # w = WavefrontObjReader("../../assets/models/testCube.obj")
            m = list(w._object.values())
            shapes = []
            l = 0
            for obj in m:
                s = Shape(p, 8)
                v = obj.vertices
                i = obj.indices
                i = [x + l for x in i]
                s.addVertices(v, i)
                l += len(v)//8

            p.draw()
            return p
    UtilsApp().run()


