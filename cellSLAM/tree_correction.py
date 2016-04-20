#===============================================================================
# Copyright (c) 2016, Max Zwiessele
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of paramz.core.constrainable nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================

from .distance_correction import ManifoldCorrection
from . import distances

class ManifoldCorrectionTree(ManifoldCorrection):

    def __init__(self, gplvm, distance=distances.mean_embedding_dist, dimensions=None):
        """
        Construct a correction class for the BayesianGPLVM given.

        This correction uses a knn-graph object in order to go along
        the cellSLAM.

        All evaluations on this object are lazy, so do not change attributes
        at runtime in order to have a consistent model.

        You can add the minimal spanning tree in, in order to
        ensure a fully connected graph. This only adds edges which are not already there,
        so that the connections are made.

        :param [GPy.models.BayesianGPLVM,GPy.models.GPLVM] gplvm:
            an optimized GPLVM or BayesianGPLVM model from GPy
        :param int k: number of neighbours to use for this knn-graph correction
        :param bool include_mst: whether to include the mst into the knn-graph [default: True]
        :param func dist: dist(X,G), the distance to use for pairwise distances
            in X using the cellSLAM embedding G
        """
        super(ManifoldCorrectionTree, self).__init__(gplvm, distance, dimensions=dimensions)

    @property
    def graph(self):
        return self.minimal_spanning_tree

    def tree_pseudo_time(self, start):
        """
        Returns the pseudo times along the tree correction of the cellSLAM
        for the given starting point `start` to all other points (including `start`).

        If the starting point is not a leaf, we will select a direction randomly
        and go backwards in time for one direction and forward for the other.

        :param int start: The index of the starting point in self.X
        """
        D = self.tree_corrected_distances
        preds = self._corrected_distances[1]
        junc = []
        left = -9999
        for _tmp in preds[:,start]:
            if _tmp != -9999:
                if _tmp not in junc:
                    junc.append(_tmp)
                    #left = junc[0]
            if len(junc) == 2:
                if ((preds[:,0]==junc[0]).sum() > (preds[:,0]==junc[1]).sum()):
                    left = junc[1]
                else:
                    left = junc[0]
                break
        pseudo_time = D[start]
        if left != -9999:
            pseudo_time[preds[:,start]==left] *= -1
        return pseudo_time

