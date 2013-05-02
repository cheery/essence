GL_VERTEX_SHADER:
    
    uniform vec2 resolution;
    
    attribute vec2 position;
    attribute vec2 texcoord;
    attribute vec4 color;

    varying vec2 _texcoord;
    varying vec4 _color;

    void main() {
        vec2 co = position / resolution - 0.5;
        gl_Position = vec4(co.x, -co.y, 0.0, 0.5);
        _texcoord   = texcoord;
        _color      = color;
    }


GL_FRAGMENT_SHADER:
    
    uniform sampler2D texture;

    varying vec2 _texcoord;
    varying vec4 _color;

    void main() {
        gl_FragColor = texture2D(texture, _texcoord) * _color;
    }
