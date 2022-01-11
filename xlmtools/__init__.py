# **************************************************************************
# *
# * Authors:     David Herreros Calero (dherreros@cnb.csic.es) [1]
# *
# * [1] National Center for Biotechnology (CSIC)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

import pwem
import pyworkflow.utils as pwutils

import xlmtools.constants as xlmConst

__version__ = "1.0.0"
_logo = "xlmtools_logo.jpg"
_references = ['Sinnott2020']
_url = "https://github.com/scipion-em/scipion-em-xlmtools"


SCRATCHDIR = pwutils.getEnvVariable('SPOCSCRATCHDIR', default='/tmp/')


class Plugin(pwem.Plugin):
    _homeVar = xlmConst.XLMTOOLS_HOME
    _pathVars = [xlmConst.XLMTOOLS_HOME]
    _supportedVersions = [xlmConst.V_CB]

    @classmethod
    def _defineVariables(cls, version=xlmConst.V_CB):
        cls._defineEmVar(xlmConst.XLMTOOLS_HOME, 'xlmtools-' + version)

    @classmethod
    def getEnviron(cls):
        pass

    @classmethod
    def getActiveVersion(cls, home=None, versions=None):
        home = os.path.basename(home or cls.getHome())
        versions = versions or cls.getSupportedVersions()
        currentVersion = home.split('-')[-1]

        for v in versions:
            if v == currentVersion:
                return v

        return ''

    @classmethod
    def isVersion(cls, version=xlmConst.V_CB):
        return cls.getActiveVersion() == version

    @classmethod
    def getEmanActivation(cls, version=xlmConst.V_CB):
        return "conda activate xlmtools-" + version

    @classmethod
    def getProgram(cls, program):
        """ Return the program binary that will be used. """
        program = os.path.join(cls.getHome('xlmtools-source'), program)
        cmd = '%s %s && python ' % (cls.getCondaActivationCmd(), cls.getEmanActivation())
        return cmd + '%(program)s ' % locals()

    @classmethod
    def getXlmtoolsCommand(cls, program, args):
        return cls.getProgram(program) + args

    @classmethod
    def defineBinaries(cls, env):
        def getCondaInstallation(version=xlmConst.V_CB):
            installationCmd = cls.getCondaActivationCmd()
            installationCmd += 'conda create -y -n xlmtools-' + version + ' python=3.6 numpy biopython scipy setuptools' + ' && '
            installationCmd += 'conda activate xlmtools-' + version + ' && '
            installationCmd += 'cd xlmtools-source' + ' && '
            installationCmd += 'python setup.py install && '
            installationCmd += 'touch xlmtools_installed'
            return installationCmd

        # For XML-CB
        xmlCB_commands = []
        xmlCB_commands.append(('wget -c https://github.com/Topf-Lab/XLM-Tools/archive/%s.tar.gz' % xlmConst.COMMIT,
                                "%s.tar.gz" % xlmConst.COMMIT))
        xmlCB_commands.append(("tar -xvf %s.tar.gz" % xlmConst.COMMIT, []))
        xmlCB_commands.append(("mv XLM*/ xlmtools-source", "xlmtools-source"))
        installationCmd_CB = getCondaInstallation(xlmConst.V_CB)
        xmlCB_commands.append((installationCmd_CB, "xlmtools-source/xlmtools_installed"))
        xmlCB_commands.append(("rm xlmtoosl-source/DEPTH", []))
        xmlCB_commands.append(("curl -O -J -L http://cospi.iiserpune.ac.in/depth/download_depth/depth",
                               ['depth_source.tar.gz']))
        xmlCB_commands.append(("tar -xvzf depth_source.tar.gz", []))
        xmlCB_commands.append(("cd depth_source/bin && make", ['depth_source/bin/DEPTH']))


        env.addPackage('xlmtools', version=xlmConst.V_CB,
                       commands=xmlCB_commands,
                       tar='void.tgz',
                       default=True)
