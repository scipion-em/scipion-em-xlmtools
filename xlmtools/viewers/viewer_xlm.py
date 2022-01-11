# **************************************************************************
# *
# * Authors:  David Herreros Calero (dherreros@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************


import os

import pyworkflow.viewer as pwviewer
import pyworkflow.protocol.params as params
import pyworkflow.utils as pwutils

import pwem.viewers.views as vi
from pwem.viewers import ChimeraView

from xlmtools.protocols.protocol_wlm import ProtWLM


class XmlViewer(pwviewer.ProtocolViewer):
    """ Visualize a PDB and its crosslinks """
    _label = 'viewer pdb crosslinks'
    _targets = [ProtWLM]
    _environments = [pwviewer.DESKTOP_TKINTER, pwviewer.WEB_DJANGO]
    OPEN_FILE = "open %s\n"


    def _defineParams(self, form):
        self.outputs = [attrName for attrName, _ in self.protocol.iterOutputAttributes()]
        form.addSection(label='Show crosslinks')
        form.addParam('doShowPDB', params.EnumParam, choices=self.outputs,
                      default=0,
                      label="Choose output to display")

    def _getVisualizeDict(self):
        return {'doShowPDB': self._doShowPDB}

    def _doShowPDB(self, obj, **kwargs):
        pdb = getattr(self.protocol, self.outputs[self.doShowPDB.get()])
        crosslink_file = pdb.getFileName()
        pdb_file = self.protocol._getExtraPath(pwutils.removeBaseExt(crosslink_file).split('_crosslinks')[0] + '.pdb')
        scriptFile = self.protocol._getPath('show_pdb_chimera.cxc')
        fhCmd = open(scriptFile, 'w')
        crosslink_file = os.path.abspath(crosslink_file)
        pdb_file = os.path.abspath(pdb_file)

        fhCmd.write(self.OPEN_FILE % crosslink_file)
        fhCmd.write(self.OPEN_FILE % pdb_file)
        # fhCmd.write("start Model Panel\n")
        fhCmd.write("show cartoons\n")
        fhCmd.write("cartoon style width 1.5 thick 1.5\n")
        fhCmd.write("style stick\n")
        fhCmd.write("color bymodel\n")
        fhCmd.close()

        view = ChimeraView(scriptFile)
        return [view]
