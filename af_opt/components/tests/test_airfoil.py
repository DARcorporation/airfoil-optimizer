import itertools
import numpy as np
import unittest

from parameterized import parameterized

from af_opt.components.airfoil import coords2cst, cst2coords


class TestCST2Coords(unittest.TestCase):
    def setUp(self) -> None:
        coords = np.loadtxt("clark-y.dat")
        i_le = np.argwhere(coords[:, 0] <= 0)[0, 0]
        coords_u = np.flipud(coords[: i_le + 1])
        coords_l = coords[i_le:]

        self.x = np.unique(np.concatenate((coords_u[:, 0], coords_l[:, 0])))
        self.y_u = np.interp(self.x, coords_u[:, 0], coords_u[:, 1])
        self.y_l = np.interp(self.x, coords_l[:, 0], coords_l[:, 1])
        self.y_c = (self.y_u + self.y_l) / 2
        self.t = self.y_u - self.y_l

    @parameterized.expand(
        [
            (f"n_ca={n[0]}, n_th={n[1]}", n[0], n[1])
            for n in itertools.product((3, 6, 12), (3, 6, 12))
        ]
    )
    def test(self, _, n_ca, n_th):
        a_ca, a_th, t_te = coords2cst(self.x, self.y_u, self.y_l, n_ca, n_th)
        x, y_u, y_l, y_c, t = cst2coords(a_ca, a_th, t_te)

        estimates = (np.interp(self.x, x, data) for data in (x, y_u, y_l, y_c, t))
        errors = (
            estimate - (self.x, self.y_u, self.y_l, self.y_c, self.t)[i]
            for i, estimate in enumerate(estimates)
        )
        rmses = (np.sqrt(np.mean(error ** 2)) for error in errors)

        for rms in rmses:
            self.assertAlmostEqual(rms, 0, 2)
