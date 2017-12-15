header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;
'''


particle_shader = header + '''
uniform vec2 resolution;
uniform float time;
uniform vec2 offsets;

void main(void)
{
   float x = gl_FragCoord.x;
   float y = gl_FragCoord.y;
   float xs = (10.0*(x-offsets.x)) / resolution.x;
   float ys = (10.0*(y-offsets.y)) / resolution.x;
   float circle = xs*xs + ys*ys;
   float r = 5.0*sqrt(xs*xs + ys*ys)*abs(0.5*sin(time*4.0)+2.0);
   //float energy = (1.0-circle)/(1.25*abs(sin(time*4.0)));
   gl_FragColor = vec4(1.0/r, 1.0/r, 1.0, 1.0/r);
}
'''

lamp_shader = header + '''
uniform vec2 resolution;
uniform float time;
uniform vec2 offsets;

void main(void)
{
   float x = gl_FragCoord.x;
   float y = gl_FragCoord.y;
   float xs = (10.0*(x+time-offsets.x)) / resolution.x;
   float ys = (10.0*(y+time-offsets.y)) / resolution.x;
   float circle = xs*xs + ys*ys;
   float r = sqrt(xs*xs/2.0 + ys*ys)*(0.05*cos(0.14159*time)+1.0);
   float energy = (1.0-circle)/(1.25*abs(sin(time*4.0)));
   gl_FragColor = vec4(1., 1., 2.0/r, 2.5/r/r);
}
'''

test_fragment_shader = """
#ifdef GL_ES
    precision highp float;
#endif
varying vec4 frag_color;
void main(void)
{
    //gl_FragColor = vec4(gl_FragCoord.x/80000., 0.0, abs(gl_FragCoord.z)/600.0, 0.5);
    //gl_FragColor = frag_color;//vec4(1.0, 1.0, 1.0, 1.0);
    float offset = gl_FragCoord.z + 100.0/800.0;
    float dark = offset*offset;
    float x = (gl_FragCoord.x + 400)/ 800;
    float y = (gl_FragCoord.y + 300)/ 600;
    
    gl_FragColor = vec4( x*dark, dark, y*dark, 1.0);
}
"""

test_vertex_shader = """
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
//varying vec2 tex_coord0;

/* vertex attributes */
attribute vec3     vPosition;
attribute vec3  vColor;
//attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
//uniform vec4       color;
uniform float      time;
void main(void)
{
    float roll=3.14159/180.0*25.0, pitch=3.14159/180.0*45.*time, yaw=3.14159/180.0*0.0*time;
    float distance = time*100/800.0;
    float view = 1; //distance*distance;
    mat4 translate = mat4(
                        view, 0.0, 0.0, 400.0,
                        0.0, view, 0.0, 300.0,
                        0.0, 0.0, 1.0/800.0, -0.1, //-0.9+distance,
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
    vec4 pos = vec4(vPosition.xyz, 1.0) * rotateY * rotateZ * rotateX * translate;
    gl_Position = projection_mat * modelview_mat * pos;
    frag_color = vec4(vColor.xyz, 1.0);
}
"""

ENERGY_VERTEX_SHADER = """
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec2 centerPOS;

/* vertex attributes */
attribute vec2 vPosition;
attribute vec2 vTexCoords0;
attribute vec2 vCenter;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform float      time;
void main(void)
{
    centerPOS = vCenter;
    vec4 pos = vec4(vPosition, 1.0, 1.0);
    gl_Position = projection_mat * modelview_mat * pos;
}
"""

ENERGY_FRAGMENT_SHADER = """
#ifdef GL_ES
    precision highp float;
#endif

varying vec2 centerPOS;
uniform float      time;
void main(void)
{
    float freq = 10.;
    float x_offset = abs(centerPOS.x - gl_FragCoord.x)/20.;
    float y_offset = abs(centerPOS.y - gl_FragCoord.y)/20.;
    float r = sqrt(x_offset * x_offset + y_offset * y_offset);
    //gl_FragColor = vec4(0./r/r, 0./r/r, 1./r/r, (0.2*sin(freq*time)+.5)/r/r/r); 
    //gl_FragColor = vec4(1., 1., 1., 1.);
    float radial = (0.2*sin(r*freq/4. - time*4.)+0.5);//r/r;
    gl_FragColor = vec4( 0.2*radial,  radial, radial, radial/r/r);//(0.2*sin(freq*time)+.5)/r/r/r);
}
"""


PROTON_FS = """
#ifdef GL_ES
    precision highp float;
#endif

varying vec2 centerPOS;
varying vec4 color;

uniform float time;
uniform vec2 pSize;
void main(void)
{
    float freq = 10.;
    float x_offset = 2.*abs(centerPOS.x - gl_FragCoord.x)/pSize.x;
    float y_offset = 2.*abs(centerPOS.y - gl_FragCoord.y)/pSize.y;
    float r = sqrt(x_offset * x_offset + y_offset * y_offset);
    gl_FragColor =   + vec4(color.xyz/r, (0.2*sin(time*freq) + 0.8)/r/r/r);
}
"""


PROTON_VS = """
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec2 centerPOS;
varying vec4 color;

/* vertex attributes */
attribute vec2 vPosition;
attribute vec2 vTexCoords0;
attribute vec2 vCenter;
attribute vec3 vColor;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform float      time;
void main(void)
{
    centerPOS = vCenter;
    color = vec4(vColor.xyz, 0.0);
    vec4 pos = vec4(vPosition, 1.0, 1.0);
    gl_Position = projection_mat * modelview_mat * pos;
}
"""

ANGLE_VS = """
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 FragPos;
varying vec3 norm;

/* vertex attributes */
attribute vec3 vPosition;
attribute vec2 vTexCoords0;
attribute vec3 vAngle;
attribute vec2 vOffsets;
attribute vec3 vNorm;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform float      time;
void main(void)
{
    float view = 1.;
    float roll = vAngle.x, pitch=vAngle.y, yaw=vAngle.z+0.;
    
    mat4 translate = mat4(
                        1.0, 0.0, 0.0, vOffsets.x,
                        0.0, 1.0, 0.0, vOffsets.y,
                        0.0, 0.0, 1.0/800, -0., //-0.9+distance,
                        0.0, 0.0, 0.0, 1.01
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
    vec4 pos = vec4(vPosition.xyz, 1.0) * rotateZ * rotateY * rotateX * translate;
    FragPos = modelview_mat * pos;
    vec4 temp = vec4(vNorm, 1.0) * rotateZ * rotateY * rotateX;
    norm = normalize(temp.xyz);
    gl_Position = projection_mat * modelview_mat *  pos ;
}
"""

ANGLE_FS = """
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 FragPos;
varying vec3 norm;

uniform float time;
uniform vec2 pSize;
uniform mat4 normal_mat;
void main(void)
{
    vec4 light;
    vec4 temp = normalize( normal_mat * vec4(norm, 0.0) );
    //norm = temp.xyz;
    float diffuse = 0.4;
    //gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    
    light = normalize(vec4(100. - 00., 400.-0., 0.+0., 0.) - FragPos);
    float directional = 1.0*max( dot(light.xyz, norm), 0.0);
    vec3 total =  diffuse * vec3(1.0, 1.0, 1.0) + directional * vec3(1.0, 1.0, 1.0);
    gl_FragColor = diffuse * vec4(1.,1.,1.,1.) *vec4(.5, 0.7, 0.9, 1.0) + 
                    directional*vec4(.9,.9,0.2,1.) *vec4(.0, 0.2, 0.5, 1.0) ; 
}
"""

