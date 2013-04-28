    precision highp float;

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
    
    uniform sampler2DMS texture;
    uniform int sample_count;

    varying vec2 _texcoord;
    varying vec4 _color;

    void main() {
        vec4 color = vec4(0.0);
        ivec2 itc = ivec2(textureSize(texture) * _texcoord);
        for (int i = 0; i < sample_count; i++) {
            color += texelFetch(texture, itc, i);
        }
        gl_FragColor = color / sample_count;
    }
