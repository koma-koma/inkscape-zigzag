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
#
"""
Description of this extension
"""
import math
import inkex

from inkex import bezier, PathElement, CubicSuperPath


class ZigZag(inkex.EffectExtension):
    """Please rename this class, don't keep it unnamed"""

    def add_arguments(self, pars):
        pars.add_argument(
            "--segments",
            type=int,
            default=2,
            help="Number of segments to divide the path into",
        )

    def effect(self):
        for node in self.svg.selection.filter(PathElement):
            new = []
            # node.style['stroke-width'] = len(node.path)
            for sub in node.path.to_superpath():
                new.append([sub[0][:]])
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
            # node.path = CubicSuperPath(new).to_path(curves_only=False)
            path = CubicSuperPath(new)
            for subpath in path:
                closed = subpath[0] == subpath[-1]
                for index, csp in enumerate(subpath):
                    if closed and index == len(subpath) - 1:
                        subpath[index] = subpath[0]
                        break
                    delta = []
                    if index % 2 == 0:
                        delta = [0, 10]
                    else:
                        delta = [0, -10]
                    csp[0][0] += delta[0]
                    csp[0][1] += delta[1]
                    csp[1][0] += delta[0]
                    csp[1][1] += delta[1]
                    csp[2][0] += delta[0]
                    csp[2][1] += delta[1]
            node.path = path


if __name__ == '__main__':
    ZigZag().run()
