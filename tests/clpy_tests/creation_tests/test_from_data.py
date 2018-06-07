import unittest

import clpy
from clpy import backend
from clpy import testing
import numpy


@testing.gpu
class TestFromData(unittest.TestCase):

    _multiprocess_can_split_ = True

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array(self, xp, dtype, order):
        return xp.array([[1, 2, 3], [2, 3, 4]], dtype=dtype, order=order)

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_from_numpy(self, xp, dtype, order):
        a = testing.shaped_arange((2, 3, 4), numpy, dtype)
        return xp.array(a, order=order)

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_copy(self, xp, dtype, order):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        return xp.array(a, order=order)

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_copy_is_copied(self, xp, dtype, order):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        b = xp.array(a, order=order)
        a.fill(0)
        return b

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes(name='dtype1', no_complex=True)
    @testing.for_all_dtypes(name='dtype2')
    @testing.numpy_clpy_array_equal()
    def test_array_copy_with_dtype(self, xp, dtype1, dtype2, order):
        # complex to real makes no sense
        a = testing.shaped_arange((2, 3, 4), xp, dtype1)
        return xp.array(a, dtype=dtype2, order=order)

    @testing.for_orders('CFAK')
    @testing.numpy_clpy_array_equal()
    def test_array_copy_with_dtype_being_none(self, xp, order):
        a = testing.shaped_arange((2, 3, 4), xp)
        return xp.array(a, dtype=None, order=order)

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_no_copy(self, xp, dtype, order):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        b = xp.array(a, copy=False, order=order)
        a.fill(0)
        return b

    @testing.for_orders('CFAK')
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_f_contiguous_input(self, xp, dtype, order):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        a = xp.asfortranarray(a)
        b = xp.array(a, copy=False, order=order)
        return b

    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_f_contiguous_output(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        b = xp.array(a, copy=False, order='F')
        self.assertTrue(b.flags.f_contiguous)
        return b

    @testing.multi_gpu(2)
    def test_array_multi_device(self):
        with backend.Device(0):
            x = testing.shaped_arange((2, 3, 4), clpy, dtype='f')
        with backend.Device(1):
            y = clpy.array(x)
        self.assertIsInstance(y, clpy.ndarray)
        self.assertIsNot(x, y)  # Do copy
        self.assertEqual(int(x.device), 0)
        self.assertEqual(int(y.device), 1)
        testing.assert_array_equal(x, y)

    @testing.multi_gpu(2)
    def test_array_multi_device_zero_size(self):
        with backend.Device(0):
            x = testing.shaped_arange((0,), clpy, dtype='f')
        with backend.Device(1):
            y = clpy.array(x)
        self.assertIsInstance(y, clpy.ndarray)
        self.assertIsNot(x, y)  # Do copy
        self.assertIsNone(x.device)
        self.assertIsNone(y.device)
        testing.assert_array_equal(x, y)

    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_array_no_copy_ndmin(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        b = xp.array(a, copy=False, ndmin=5)
        self.assertEqual(a.shape, (2, 3, 4))
        a.fill(0)
        return b

    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_asarray(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        return xp.asarray(a)

    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_asarray_is_not_copied(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)
        b = xp.asarray(a)
        a.fill(0)
        return b

    def test_ascontiguousarray_on_noncontiguous_array(self):
        a = testing.shaped_arange((2, 3, 4))
        b = a.transpose(2, 0, 1)
        c = clpy.ascontiguousarray(b)
        self.assertTrue(c.flags.c_contiguous)
        testing.assert_array_equal(b, c)

    def test_ascontiguousarray_on_contiguous_array(self):
        a = testing.shaped_arange((2, 3, 4))
        b = clpy.ascontiguousarray(a)
        self.assertIs(a, b)

    @testing.for_CF_orders()
    @testing.for_all_dtypes()
    @testing.numpy_clpy_array_equal()
    def test_copy(self, xp, dtype, order):
        a = xp.zeros((2, 3, 4), dtype=dtype)
        b = xp.copy(a, order=order)
        a[1] = 1
        return b

    @testing.multi_gpu(2)
    @testing.for_CF_orders()
    @testing.for_all_dtypes()
    def test_copy_multigpu(self, dtype, order):
        with backend.Device(0):
            src = clpy.random.uniform(-1, 1, (2, 3)).astype(dtype)
        with backend.Device(1):
            dst = clpy.copy(src, order)
        testing.assert_allclose(src, dst, rtol=0, atol=0)

    @testing.for_CF_orders()
    @testing.numpy_clpy_equal()
    def test_copy_order(self, xp, order):
        a = xp.zeros((2, 3, 4), order=order)
        b = xp.copy(a)
        return (b.flags.c_contiguous, b.flags.f_contiguous)


@testing.parameterize(
    *testing.product({
        'ndmin': [0, 1, 2, 3],
        'copy': [True, False],
        'xp': [numpy, clpy]
    })
)
class TestArrayPreservationOfShape(unittest.TestCase):

    @testing.for_all_dtypes()
    def test_clpy_array(self, dtype):
        shape = 2, 3
        a = testing.shaped_arange(shape, self.xp, dtype)
        clpy.array(a, copy=self.copy, ndmin=self.ndmin)

        # Check if clpy.ndarray does not alter
        # the shape of the original array.
        self.assertEqual(a.shape, shape)


@testing.parameterize(
    *testing.product({
        'ndmin': [0, 1, 2, 3],
        'copy': [True, False],
        'xp': [numpy, clpy]
    })
)
class TestArrayCopy(unittest.TestCase):

    @testing.for_all_dtypes()
    def test_clpy_array(self, dtype):
        a = testing.shaped_arange((2, 3), self.xp, dtype)
        actual = clpy.array(a, copy=self.copy, ndmin=self.ndmin)

        should_copy = (self.xp is numpy) or self.copy
        # TODO(Kenta Oono): Better determination of copy.
        is_copied = not ((actual is a) or (actual.base is a) or
                         (actual.base is a.base and a.base is not None))
        self.assertEqual(should_copy, is_copied)


class TestArrayInvalidObject(unittest.TestCase):

    def test_invalid_type(self):
        a = numpy.array([1, 2, 3], dtype=object)
        with self.assertRaises(ValueError):
            clpy.array(a)