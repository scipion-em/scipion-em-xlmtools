# **************************************************************************
# *
# * Authors:     David Herreros Calero (dherreros@cnb.csic.es)
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


from os.path import abspath, join

from pwem.objects import AtomStruct
from pwem.protocols import ProtAnalysis3D

from pyworkflow.protocol import MultiPointerParam, IntParam, PathParam
from pyworkflow import BETA
import pyworkflow.utils as pwutils

import xlmtools


class ProtWLM(ProtAnalysis3D):
    """
    Wrapper for XLM Tools to score model protein structures according to crosslink and monolink data
    """
    _label = 'xlm'
    _devStatus = BETA

    # --------------------------- DEFINE param functions ------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('xlList', PathParam,
                      label='XL list', important=True,
                      help='Input list of crosslinks and monolinks')
        form.addParam('pdbs', MultiPointerParam, pointerClass="AtomStruct",
                      label='Atomic structure', important=True)
        form.addSection(label='Jwalk')
        form.addParam('vox', IntParam, allowsNull=True,
                      label='Voxel size', help="Specify voxel size of grid.")
        # form.addParallelSection(threads=4, mpi=0)


    # --------------------------- INSERT steps functions ------------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.convertStep)
        self._insertFunctionStep(self.computeControlStep)
        self._insertFunctionStep(self.createOutputStep)

    # --------------------------- STEPS functions -------------------------------
    def convertStep(self):
        self.extra_files = []
        for atomstruct in self.pdbs:
            ori_file = atomstruct.get().getFileName()
            dest_file = pwutils.removeBaseExt(ori_file) + '.pdb'
            pwutils.createLink(ori_file, self._getExtraPath(dest_file))
            self.extra_files.append(dest_file)

    def computeControlStep(self):
        depth_source = join(xlmtools.Plugin.getHome('depth_source/'), 'bin', 'DEPTH')
        args = '-xl_list %s -jwalk -depth -depth_source %s -pdb ' % (abspath(self.xlList.get()),
                                                                     depth_source)

        args += ' '.join(self.extra_files) + ' '

        if self.vox.get():
            args += '-vox %d' % self.vox.get()

        program = xlmtools.Plugin.getProgram("xlmtools.v1.0.py")
        self.runJob(program, args, cwd=self._getExtraPath())

    def createOutputStep(self):
        for idf, file in enumerate(self.extra_files):
            crosslinks_file = self._getExtraPath(join('Jwalk_results', pwutils.removeBaseExt(file) + '_crosslinks.pdb'))
            atomstruct = AtomStruct()
            atomstruct.setFileName(crosslinks_file)
            args = {'crosslinkStruct_%d' % (idf + 1): atomstruct}
            self._defineOutputs(**args)
            self._defineSourceRelation(self.pdbs[idf], atomstruct)

    # --------------------------- INFO functions ------------------------------
    def _methods(self):
        methods = []
        methods.append('XLM Tools tools: A tool to score model protein structures '
                       'according to crosslink and monolink data.')
        return methods

    def _summary(self):
        summary = []
        if not self.isFinished():
            summary.append("Scoring not ready yet")

        if self.getOutputsSize() >= 1:
            stdout = self._getLogsPath('run.stdout')
            with open(stdout) as file:
                for num, line in enumerate(file, 1):
                    if 'Resolution at 1 % FDR-FSC' in line:
                        res = [float(s) for s in line.split() if s.replace(".", "", 1).isdigit()][1]
            summary.append('Resolution at 1 %% FDR-FSC: %.2f Angstrom' % res)
        return summary
