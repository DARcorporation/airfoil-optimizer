#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the OpenMDAO Model of the airfoil optimization problem.
"""
import numpy as np
import openmdao.api as om

from .components import *


class AfOptModel(om.Group):
    """
    Airfoil shape optimization using XFoil.
    """

    def initialize(self):
        self.options.declare("n_ca", default=6, types=int)
        self.options.declare("n_th", default=6, types=int)
        self.options.declare("fix_te", default=True, types=bool)

        self.options.declare("n_area_bins", default=5, lower=1, types=int)

        self.options.declare(
            "t_te_min", default=0.0, lower=0.0, types=float, allow_none=False
        )
        self.options.declare("t_c_min", default=0.1, types=float, allow_none=True)
        self.options.declare("r_le_min", default=0.05, types=float, allow_none=True)
        self.options.declare("A_cs_min", default=0.1, types=float, allow_none=True)
        self.options.declare("A_bins_min", default=0.02, types=float, allow_none=True)
        self.options.declare("Cm_max", default=None, types=float, allow_none=True)

        self.options.declare("n_coords", default=100, types=int)

    def setup(self):
        # Number of CST coefficients
        n_ca = self.options["n_ca"]
        n_th = self.options["n_th"]

        # Number of bins to check for slender sections
        n_area_bins = self.options["n_area_bins"]

        # Design variable bounds
        a_c_lower = -0.25 * np.ones(n_ca)
        a_c_upper = +0.25 * np.ones(n_ca)
        a_t_lower = +0.01 * np.ones(n_th)
        a_t_upper = +0.20 * np.ones(n_th)
        t_te_upper = 0.1

        # Independent variables
        ivc = om.IndepVarComp()
        ivc.add_output("a_ca", val=np.zeros(n_ca))
        ivc.add_output("a_th", val=np.zeros(n_th))
        ivc.add_output("t_te", val=self.options["t_te_min"])
        ivc.add_output("Re", val=1e6)
        ivc.add_output("M", val=0.0)
        ivc.add_output("Cl_des", val=1.0)

        # Main sub-systems
        self.add_subsystem("ivc", ivc, promotes=["*"])
        self.add_subsystem("XFoil", XFoilAnalysis(n_ca=n_ca, n_th=n_th), promotes=["*"])

        # Design variables
        self.add_design_var("a_ca", lower=a_c_lower, upper=a_c_upper)
        self.add_design_var("a_th", lower=a_t_lower, upper=a_t_upper)

        if not self.options["fix_te"]:
            self.add_design_var(
                "t_te", lower=self.options["t_te_min"], upper=t_te_upper
            )

        # Objective
        self.add_objective("Cd")  # Cd

        # Constraints
        self.add_subsystem("Geometry", Geometry(n_ca=n_ca, n_th=n_th, n_area_bins=n_area_bins), promotes=["*"])

        if self.options["t_c_min"] is not None:
            self.add_subsystem(
                "G1",
                om.ExecComp(
                    f"g1 = 1 - t_c / {self.options['t_c_min']:15g}", g1=0.0, t_c=1.0
                ),
                promotes=["*"],
            )
            self.add_constraint("g1", upper=0.0)  # t_c >= t_c_min

        if self.options["r_le_min"] is not None:
            self.add_subsystem(
                "G2",
                om.ExecComp(
                    f"g2 = 1 - r_le / {self.options['r_le_min']:15g}", g2=0.0, r_le=1.0
                ),
                promotes=["*"],
            )
            self.add_constraint("g2", upper=0.0)  # r_le >= r_le_min

        if self.options["A_cs_min"] is not None:
            self.add_subsystem(
                "G3",
                om.ExecComp(
                    f"g3 = 1 - A_cs / {self.options['A_cs_min']:15g}", g3=0, A_cs=1.0
                ),
                promotes=["*"],
            )
            self.add_constraint("g3", upper=0.0)  # A_cs >= A_cs_min

        if self.options["A_bins_min"] is not None:
            self.add_subsystem(
                "G4",
                om.ExecComp(
                    f"g4 = 1 - A_bins / {self.options['A_bins_min']:15g}",
                    g4=np.zeros(n_area_bins),
                    A_bins=np.ones(n_area_bins),
                ),
                promotes=["*"],
            )
            self.add_constraint("g4", upper=0.0)  # A_bins >= A_bins_min

        if self.options["Cm_max"] is not None:
            self.add_subsystem(
                "G5",
                om.ExecComp(
                    f"g5 = 1 - abs(Cm) / {np.abs(self.options['Cm_max']):15g}",
                    g5=0.0,
                    Cm=1.0,
                ),
                promotes=["*"],
            )
            self.add_constraint("g5", lower=0.0)  # |Cm| <= |Cm_max|

    def __repr__(self):
        outputs = dict(self.list_outputs(out_stream=None))

        s_t_te_des = f"{outputs['ivc.t_te']['value'][0]:.4g}"
        desvar_formatter = {"float_kind": "{: 7.4f}".format}

        s_area_bins = np.array2string(
            outputs["Geometry.A_bins"]["value"],
            formatter=desvar_formatter,
            separator=", ",
        )
        s_a_ca = np.array2string(
            outputs["ivc.a_ca"]["value"], formatter=desvar_formatter, separator=", "
        )
        s_a_th = np.array2string(
            outputs["ivc.a_th"]["value"], formatter=desvar_formatter, separator=", "
        )

        yaml = ""
        yaml += f"Cl: {outputs['ivc.Cl_des']['value'][0]:.4g}\n"
        yaml += f"M: {outputs['ivc.M']['value'][0]:.4g}\n"
        yaml += f"Re: {outputs['ivc.Re']['value'][0]:.4g}\n"
        yaml += (
            "" if self.options["fix_te"] else "min "
        ) + f"t_te: {self.options['t_te_min']:.4g}\n"
        if self.options["t_c_min"] is not None:
            yaml += f"t_c_min: {self.options['t_c_min']:.4g}\n"
        if self.options["r_le_min"] is not None:
            yaml += f"r_le_min: {self.options['r_le_min']:.4g}\n"
        if self.options["A_cs_min"] is not None:
            yaml += f"A_cs_min: {self.options['A_cs_min']:.4g}\n"
        if self.options["A_bins_min"] is not None:
            yaml += f"A_bins_min: {self.options['A_bins_min']:.4g}\n"
        if self.options["Cm_max"] is not None:
            yaml += f"Cm_max: {self.options['Cm_max']:.4g}\n"
        yaml += f"Cd: {outputs['XFoil.Cd']['value'][0]:.4g}\n"
        yaml += f"Cm: {outputs['XFoil.Cm']['value'][0]: .4g}\n"
        yaml += f"t_c: {outputs['Geometry.t_c']['value'][0]:.4g}\n"
        yaml += f"r_le: {outputs['Geometry.r_le']['value'][0]:.4g}\n"
        yaml += f"A_cs: {outputs['Geometry.A_cs']['value'][0]:.4g}\n"
        yaml += f"A_bins: {s_area_bins}\n"
        yaml += f"a_ca: {s_a_ca}\n"
        yaml += f"a_th: {s_a_th}"
        if not self.options["fix_te"]:
            yaml += f"\nt_te: {s_t_te_des}"

        return yaml
