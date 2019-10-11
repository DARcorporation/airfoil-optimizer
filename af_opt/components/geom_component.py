#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the definition of the Airfoil Geometry OpenMDAO Component.
"""
import numpy as np

from .airfoil_component import AirfoilComponent


class Geom(AirfoilComponent):
    """
    Computes the thickness-over-chord ratio and cross-sectional area of an airfoil.
    """

    def setup(self):
        super().setup()
        # Outputs
        self.add_output("t_c", val=0.0)
        self.add_output("A_cs", val=0.0)
        self.add_output("r_le", val=0.0)

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        x, y_u, y_l, _, t = self.compute_coords(inputs)

        outputs["t_c"] = np.max(t)
        outputs["A_cs"] = np.trapz(t, x)

        xs = np.concatenate((np.flip(x), x[1:]))
        ys = np.concatenate((np.flip(y_u), y_l[1:]))

        dx = np.gradient(xs)
        dy = np.gradient(ys)

        d2x = np.gradient(dx)
        d2y = np.gradient(dy)

        curvature = np.abs(d2x * dy - dx * d2y) / (dx * dx + dy * dy) ** 1.5
        if np.isnan(curvature[x.size]) or np.isinf(curvature[x.size]) or curvature[x.size] == 0.0:
            outputs["r_le"] = 0.0
        else:
            outputs["r_le"] = 1.0 / curvature[x.size]
