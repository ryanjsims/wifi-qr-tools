import xml.etree.ElementTree as ET
import xml
import numpy
from argparse import ArgumentParser as AP
from stl import mesh


def main():
    parser = AP(description="Convert QR path SVGs to STLs")
    parser.add_argument("svg", help="Filename of SVG to convert")
    parser.add_argument("stl", help="STL to store converted SVG")
    parser.add_argument("--background-depth", "-b", type=int, help="Depth in mm of background (Default: 5mm)", default=5)
    parser.add_argument("--foreground-depth", "-f", type=int, help="Depth in mm of foreground (Default: 3mm)", default=3)
    parser.add_argument("--scale", "-s", type=float, help="XY scale (Default: 1.0)", default = 1.0) 
    args = parser.parse_args()

    tree = ET.parse(args.svg)
    root = tree.getroot()
    dimensions = [float(elem) * args.scale for elem in root.attrib["viewBox"].split()]
    base_shape = [
            (dimensions[0], dimensions[1]), 
            (dimensions[0], dimensions[3]), 
            (dimensions[2], dimensions[3]),
            (dimensions[2], dimensions[1])
    ]
    vertices = get_vertices(iter_shapes(root, args.scale), base_shape, args)
    triangles = get_triangles(iter_shapes(root, args.scale), base_shape, vertices, args)
    vertices = numpy.array(vertices)
    triangles = numpy.array(triangles)
    qr3d = mesh.Mesh(numpy.zeros(triangles.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(triangles):
        for j in range(3):
            qr3d.vectors[i][j] = vertices[f[j],:]
    qr3d.save(args.stl)


def tokenize(dsvgstr: str, scale: float):
    dsvg = dsvgstr.split()
    i = 0
    while i < len(dsvg):
        command = dsvg[i]
        if command in "ML":
            args = (float(dsvg[i+1]) * scale, float(dsvg[i+2]) * scale)
            i += 3
        elif command in "HV":
            args = (float(dsvg(i+1)) * scale)
            i += 2
        elif command.upper() == "Z":
            args = tuple()
            i += 1
        else:
            raise ValueError("Unsupported command: {}".format(command))
        yield command.upper(), args


def iter_shapes(root, scale):
    assert len(root) == 1
    shape = []
    for command, args in tokenize(root[0].attrib["d"], scale):
        if command == "M":
            shape = [args]
        elif command == "L":
            shape.append(args)
        elif command == "H":
            args.append(shape[-1][1])
            shape.append(args)
        elif command == "V":
            shape.append([shape[-1][0], args[0]])
        elif command == "Z":
            yield shape


def get_vertices(shapes, base_shape, args):
    vertices = set()
    for shape in shapes:
        for vertex in shape:
            vertices.add(vertex + (args.background_depth,))
            vertices.add(vertex + (args.background_depth + args.foreground_depth,))
    for vertex in base_shape:
        vertices.add(vertex + (0,))
        vertices.add(vertex + (args.background_depth,))
    
    return list(vertices)


def get_triangles(shapes, base_shape, vertices, args):
    triangles = []
    for shape in shapes:
        triangles.append([
            vertices.index(shape[0] + (args.background_depth + args.foreground_depth,)),
            vertices.index(shape[3] + (args.background_depth + args.foreground_depth,)),
            vertices.index(shape[2] + (args.background_depth + args.foreground_depth,))
        ])
        triangles.append([
            vertices.index(shape[2] + (args.background_depth + args.foreground_depth,)),
            vertices.index(shape[1] + (args.background_depth + args.foreground_depth,)),
            vertices.index(shape[0] + (args.background_depth + args.foreground_depth,))
        ])
        for i in range(4):
            triangles.append([
                vertices.index(shape[i] + (args.background_depth + args.foreground_depth,)),
                vertices.index(shape[i] + (args.background_depth,)),
                vertices.index(shape[(i+1) % 4] + (args.background_depth + args.foreground_depth,))
            ])
            triangles.append([
                vertices.index(shape[i] + (args.background_depth,)),
                vertices.index(shape[(i+1) % 4] + (args.background_depth,)),
                vertices.index(shape[(i+1) % 4] + (args.background_depth + args.foreground_depth,))
            ])

    triangles.append([
        vertices.index(base_shape[0] + (0,)),
        vertices.index(base_shape[1] + (0,)),
        vertices.index(base_shape[3] + (0,))
    ])
    triangles.append([
        vertices.index(base_shape[1] + (0,)),
        vertices.index(base_shape[2] + (0,)),
        vertices.index(base_shape[3] + (0,))
    ])
    for i in range(4):
        triangles.append([
            vertices.index(base_shape[i] + (args.background_depth,)),
            vertices.index(base_shape[i] + (0,)),
            vertices.index(base_shape[(i+1) % 4] + (args.background_depth,))
        ])
        triangles.append([
            vertices.index(base_shape[i] + (0,)),
            vertices.index(base_shape[(i+1) % 4] + (0,)),
            vertices.index(base_shape[(i+1) % 4] + (args.background_depth,))
        ])
    triangles.append([
        vertices.index(base_shape[0] + (args.background_depth,)),
        vertices.index(base_shape[3] + (args.background_depth,)),
        vertices.index(base_shape[2] + (args.background_depth,))
    ])
    triangles.append([
        vertices.index(base_shape[2] + (args.background_depth,)),
        vertices.index(base_shape[1] + (args.background_depth,)),
        vertices.index(base_shape[0] + (args.background_depth,))
    ])
    return triangles

main()
