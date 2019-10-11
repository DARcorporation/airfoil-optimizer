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
        # Inputs
        self.add_input("t_min", shape=1)
        # Outputs
        self.add_output("t_c", val=0.0)
        self.add_output("A_cs", val=0.0)
        self.add_output("con_t_min", val=0.0)

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        x, _, _, _, t = self.compute_coords(inputs)
        outputs["t_c"] = np.max(t)
        outputs["A_cs"] = np.trapz(t, x)
        if inputs["t_min"] is None or inputs["t_min"] == 0.0:
            outputs["con_t_min"] = 1 - np.min(t[x >= inputs["t_min"]]) / inputs["t_min"]
        else:
            outputs["con_t_min"] = 0.0
