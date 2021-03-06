    precision highp float;
GL_VERTEX_SHADER:
    uniform vec2 resolution;
    uniform sampler2D texture;
    attribute vec2 position;
    attribute vec2 texcoord;
    attribute vec2 colorsrc;
    varying vec2 v_texcoord;
    varying vec4 v_color;
    void main() {
        gl_Position = vec4((position/resolution - 0.5)*vec2(1.0, -1.0), 0.0, 0.5);
        v_texcoord = texcoord;
        v_color = texture2D(texture, colorsrc);
    }
GL_FRAGMENT_SHADER:
    varying vec2 v_texcoord;
    varying vec4 v_color;
    uniform sampler2D texture;
    void main() {
        gl_FragColor = texture2D(texture, v_texcoord) * v_color;
    }
