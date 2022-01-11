# **************************************************************************
# *
# * Authors:    David Herreros Calero (dherreros@cnb.csic.es) [1]
# *
# * [1] Centro Nacional de Biotecnologia, CSIC, Spain
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

from os.path import join
import numpy as np

from pwem.protocols import ProtImportPdb
from pwem.convert.atom_struct import AtomicStructHandler

from pyworkflow.tests import BaseTest, setupTestProject

from xlmtools.protocols import ProtWLM
import xlmtools


class TestXLM(BaseTest):
    """This class check if WLM Tools protocol works properly"""

    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.pdb = join(xlmtools.Plugin.getHome('xlmtools-source'), 'examples', 'from_pdb', 'model185_1.pdb')
        cls.xlList = join(xlmtools.Plugin.getHome('xlmtools-source'), 'examples', 'from_pdb', 'both.txt')
        cls.gs = join(xlmtools.__path__[0], 'testdata', 'gs.pdb')

    def runImportPDBs(cls, label):
        """ Run an Import particles protocol. """
        protImport = cls.newProtocol(ProtImportPdb,
                                     inputPdbData=1,
                                     pdbFile=cls.pdb,
                                     objLabel=label)
        cls.launchProtocol(protImport)
        return protImport.outputPdb

    def runXlmTools(self, pdb):
        prot = self.newProtocol(ProtWLM, xlList=self.xlList, pdbs=[pdb])
        self.launchProtocol(prot)
        self.assertIsNotNone(prot.crosslinkStruct_1,
                             "There was a problem with WLM Tools protocol output")
        return prot

    def test_xlm_tools(self):
        pdb = self.runImportPDBs('PDB Struct')
        prot = self.runXlmTools(pdb)
        struct = prot.crosslinkStruct_1
        ah = AtomicStructHandler()

        # Get crosslink coords from test
        ah.read(struct.getFileName())
        atomIterator = ah.getStructure().get_atoms()
        coords = np.asarray([np.append(atom.get_coord(), 1) for atom in atomIterator])

        # Get crosslink coords from GS
        ah.read(self.gs)
        atomIterator = ah.getStructure().get_atoms()
        coords_gs = np.asarray([np.append(atom.get_coord(), 1) for atom in atomIterator])

        rmse = np.sqrt(np.sum((coords - coords_gs) ** 2) / coords.shape[0])
        self.assertEqual(rmse, 0.0, msg="Unexpected crosslink positions")
        return prot