#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the definition of the Airfoil Geometry OpenMDAO Component.
"""
import numpy as np

from scipy.interpolate import InterpolatedUnivariateSpline

from .airfoil import AirfoilComponent


class Geometry(AirfoilComponent):
    """
    Computes the thickness-over-chord ratio and cross-sectional area of an airfoil.
    """

    def initialize(self):
        super().initialize()
        self.options.declare(
            "n_area_bins",
            default=5,
            lower=1,
            desc="Number of 'bins' to divide to chord into."
            "For each bin, the area enclosed by the upper and lower surface will be computed"
            "as a fraction of the width of the bin. This can be used as a check to avoid very"
            "slender parts of the airfoil.",
        )

    def setup(self):
        super().setup()
        # Outputs
        self.add_output("t_c", val=0.0)
        self.add_output("A_cs", val=0.0)
        self.add_output("r_le", val=0.0)

        self.add_output(
            "A_bins",
            val=np.zeros(self.options["n_area_bins"]),
            desc="Area enclosed by the upper and lower surfaces as a fraction of the bin width.",
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        x, y_u, y_l, _, t = self.compute_coords(inputs)

        # Compute the t/c and cross-sectional area of the airfoil
        outputs["t_c"] = np.max(t)
        outputs["A_cs"] = np.trapz(t, x)

        # Compute the area, as fraction of the bin width,
        # enclosed by the upper and lower surfaces for each bin.
        f_t = InterpolatedUnivariateSpline(x, t)
        n_area_bins = self.options["n_area_bins"]
        dx_bins = 1 / n_area_bins
        outputs["A_bins"] = [
            f_t.integral(i * dx_bins, (i + 1) * dx_bins) / dx_bins
            for i in range(n_area_bins)
        ]

        # Compute the leading edge radius of the airfoil
        xs = np.concatenate((np.flip(x), x[1:]))
        ys = np.concatenate((np.flip(y_u), y_l[1:]))

        dx = np.gradient(xs)
        dy = np.gradient(ys)

        d2x = np.gradient(dx)
        d2y = np.gradient(dy)

        curvature = np.abs(d2x * dy - dx * d2y) / (dx * dx + dy * dy) ** 1.5
        if (
            np.isnan(curvature[x.size])
            or np.isinf(curvature[x.size])
            or curvature[x.size] == 0.0
        ):
            outputs["r_le"] = 0.0
        else:
            outputs["r_le"] = 1.0 / curvature[x.size]
