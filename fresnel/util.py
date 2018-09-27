# Copyright (c) 2016-2018 The Regents of the University of Michigan
# This file is part of the Fresnel project, released under the BSD 3-Clause License.

R"""
Utility classes and methods.
"""

import numpy
import io


try:
    import PIL.Image as PIL_Image;
except ImportError:
    PIL_Image = None;

class array(object):
    R""" Map internal fresnel buffers as numpy arrays.

    :py:class:`fresnel.util.array` provides a python interface to access internal data of memory buffers stored and
    managed by fresnel. These buffers may exist on the CPU or GPU depending on the device configuration, so
    :py:class:`fresnel.util.array` only allows certain operations: read/write of array data, and read-only querying of
    array properties.

    You can access a :py:class:`fresnel.util.array` as if it were a numpy array (with limited operations).

    Write to an array with ``array[slice] = v`` where *v* is a numpy array or anything that numpy can convert to an
    array. When *v* is a contiguous numpy array of the appropriate data type, the data is copied directly from *v*
    into the internal buffer.

    Read from an array with ``v = array[slice]``. This returns a **copy** of the data as a numpy array because the
    array references internal data structures in fresnel that may exist on the GPU.

    Attributes:

        shape (tuple): Dimensions of the array.
        dtype: Numpy data type
    """

    def __init__(self, buf, geom):
        self.buf = buf;
        # geom stores a pointer to the owning geometry, so array writes trigger acceleration structure updates
        # set to None if this buffer is not associated with a geometry
        self.geom = geom

    def __setitem__(self, slice, data):
        self.buf.map();
        a = numpy.array(self.buf, copy=False);
        a[slice] = data;
        self.buf.unmap();

        if self.geom is not None:
            self.geom._geometry.update();

    def __getitem__(self, slice):
        self.buf.map();
        a = numpy.array(self.buf, copy=False);
        data = numpy.array(a[slice], copy=True);
        self.buf.unmap();
        return data;

    @property
    def shape(self):
        self.buf.map();
        a = numpy.array(self.buf, copy=False);
        self.buf.unmap();
        return a.shape;

    @property
    def dtype(self):
        self.buf.map();
        a = numpy.array(self.buf, copy=False);
        self.buf.unmap();
        return a.dtype;

class image_array(array):
    R""" Map internal fresnel image buffers as numpy arrays.

    Inherits from :py:class:`array` and provides all of its functionality, plus some additional convenience methods
    specific to working with images. Images are represented as WxHx4 numpy arrays of unsigned chars in RGBA format.

    Specifically, when a :py:class:`image_array` is the result of an image in a Jupyter notebook cell, Jupyter will
    display the image.
    """

    def _repr_png_(self):
        if PIL_Image is None:
            raise RuntimeError("No PIL.Image module to format png");

        self.buf.map();

        f = io.BytesIO();
        a = numpy.array(self.buf, copy=False);
        PIL_Image.fromarray(a, mode='RGBA').save(f, 'png');
        self.buf.unmap();

        return f.getvalue();


def convex_polyhedron_from_vertices(vertices):
    R""" Convert convex polyhedron vertices to data structures that fresnel can draw.

    Args:
        vertices: The vertices of the polyhedron
          **Type:** anything convertible by numpy to a Nx2x3 array of floats.

    Returns:
        A dict containing the information used to draw the polyhedron. The dict
        contains the keys `face_origin`, `face_normal`, `face_color`, and `radius`.

    The dictionary can be used directly to draw a polyhedron from its vertices:

    .. highlight:: python
    .. code-block:: python

        scene = fresnel.Scene()
        polyhedron = fresnel.util.convex_polyhedron_from_vertices(vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(scene,
                                                     polyhedron,
                                                     position=[0, 0, 0],
                                                     orientation=[1, 0, 0, 0])

    """
    from fresnel._common import find_polyhedron_faces
    # sanity checks on the shape of things here?
    return find_polyhedron_faces(vertices)


def _get_r_circ(vertices):
    """Estimate circumsphere radius based on vertices of a polyhedron
    """
    vertices = numpy.array(vertices)
    radii = numpy.sqrt(numpy.sum(vertices**2, axis=1))
    return numpy.amax(radii)
