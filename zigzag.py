#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [YEAR] [YOUR NAME], [YOUR EMAIL]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# TODO: closedの場合の処理とsmoothの処理
#
"""
ZigZag effect for Inkscape
"""
import math
import inkex

from inkex import bezier, PathElement, CubicSuperPath


class ZigZag(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            "--segments",
            type=int,
            default=2,
            help="Number of segments to divide the path into",
        )
        pars.add_argument(
            "--size",
            type=float,
            default=0.1,
            help="Size",
        )
        pars.add_argument(
            "--type",
            default="liner",
            help="Type of line"
        )
        pars.add_argument(
            "--unit", default="px", help="Unit for size"
        )

    def effect(self):
        for node in self.svg.selection.filter(PathElement):
            new = []

            for sub in node.path.to_superpath():
                new.append([sub[0][:]])
                inkex.utils.debug(sub[0])
                i = 1
                while i <= len(sub) - 1:
                    splits = self.options.segments + 1
                    for sel in range(int(splits), 1, -1):
                        result = bezier.cspbezsplitatlength(
                            new[-1][-1], sub[i], 1.0 / sel
                        )
                        better_result = [
                            [list(el) for el in elements] for elements in result
                        ]
                        new[-1][-1], nxt, sub[i] = better_result
                        new[-1].append(nxt[:])
                    new[-1].append(sub[i])
                    i += 1

            path = CubicSuperPath(new)
            for subpath in path:
                closed = subpath[0] == subpath[-1]
                for index, csp in enumerate(subpath):
                    if closed and index == len(subpath) - 1:
                        subpath[index] = subpath[0]
                        break
                    if csp[0] == csp[1] == csp[2]:
                        a = index - 1
                        b = index + 1
                        if index == 0:
                            a = index
                        elif index == len(subpath) - 1:
                            b = index
                        vector = (subpath[b][1][0] - subpath[a][1]
                                  [0], subpath[b][1][1] - subpath[a][1][1])
                    else:
                        vector = (csp[2][0] - csp[0][0], csp[2][1] - csp[0][1])

                    if vector[0] != 0:
                        normal_vector = (-vector[1], vector[0])
                    else:
                        normal_vector = (-1, 0)

                    norm = math.sqrt(
                        normal_vector[0] ** 2 + normal_vector[1] ** 2)
                    normalized = (
                        normal_vector[0] / norm, normal_vector[1] / norm)

                    size = self.svg.viewport_to_unit(
                        f"{self.options.size}{self.options.unit}"
                    )
                    if index % 2 == 1:
                        size = -self.options.size

                    delta = [n * size for n in normalized]

                    for p in csp:
                        p[0] += delta[0]
                        p[1] += delta[1]
                    if self.options.type == "linear":
                        csp[0][0] = csp[1][0]
                        csp[0][1] = csp[1][1]
                        csp[2][0] = csp[1][0]
                        csp[2][1] = csp[1][1]

            node.path = path


if __name__ == '__main__':
    ZigZag().run()
