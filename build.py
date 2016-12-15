
import sys
import shutil
import buildsystem
import urllib.request
import gzip
import tarfile
import glob
import os
from os.path import expanduser


SOURCE_SRC_DIR     = './build/source/src/'
SOURCE_SRC_LIB_DIR = './build/source/src/lib/'


####################################################################################################
# Generate
####################################################################################################

def generate(config, aol):

    buildsystem.mkdir_p(buildsystem.TEMP_DIR)

    srctargz = buildsystem.ARCHIVE_DIR + 'jansson-2.9.tar.gz'

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(buildsystem.ARCHIVE_DIR):
            os.makedirs(buildsystem.ARCHIVE_DIR)

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = buildsystem.TEMP_DIR + 'jansson-2.9.tar.gz'
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(buildsystem.TEMP_DIR + 'jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(buildsystem.TEMP_DIR + 'jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(buildsystem.TEMP_DIR + 'jansson-2.9.tar')
    tar.extractall(buildsystem.TEMP_DIR)
    tar.close()

    shutil.copytree(buildsystem.TEMP_DIR + 'jansson-2.9', buildsystem.SOURCE_DIR)


####################################################################################################
# Configure
####################################################################################################

def configure(config, aol):

    buildsystem.mkdir_p(buildsystem.DIST_DIR)

    if aol.operatingSystem == 'windows':

        with open(SOURCE_SRC_DIR + 'jansson_private_config.h', 'w') as f:
            f.write('#define HAVE_STDINT_H  1\n')

        filename = SOURCE_SRC_DIR + 'jansson_config.h'
        shutil.copy2(SOURCE_SRC_DIR + 'jansson_config.h.in', filename)

        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin
        configureScript = 'configure'
        os.chmod(buildsystem.SOURCE_DIR + configureScript, 0o777)

        buildsystem.runProgram(config, buildsystem.SOURCE_DIR, os.environ, ['bash', configureScript, '--prefix=/usr/local'])


####################################################################################################
# Make
####################################################################################################

def make(config, aol):

    buildsystem.mkdir_p(buildsystem.OUTPUT_DIR)

    if aol.operatingSystem == 'windows':
        makefile = os.path.relpath(buildsystem.MAKE_DIR, buildsystem.OUTPUT_DIR) + '\\' + str(aol) + '.makefile'

        env = os.environ
        env['BUILD_TYPE'] = 'normal'
        env['SOURCE'] = os.path.relpath(SOURCE_SRC_DIR, buildsystem.OUTPUT_DIR)

        env['OUTPUT'] = '.'
        buildsystem.runProgram(config, buildsystem.OUTPUT_DIR, env, ['make', '-f', makefile, 'clean', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, buildsystem.SOURCE_DIR, os.environ, ['make', 'clean', 'all'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, aol):

    buildsystem.rmdir(buildsystem.DIST_DIR, buildsystem.DISTTEMP_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_DIR)

    buildsystem.mkdir_p(buildsystem.DIST_INCLUDE_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIB_SHARED_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIB_STATIC_DIR)
    buildsystem.mkdir_p(buildsystem.ARTIFACT_DIR)

    shutil.copy2(SOURCE_SRC_DIR + 'jansson.h', buildsystem.DIST_INCLUDE_DIR)
    shutil.copy2(SOURCE_SRC_DIR + 'jansson_config.h', buildsystem.DIST_INCLUDE_DIR)

    if aol.operatingSystem == 'windows':
        shutil.copy2(buildsystem.OUTPUT_DIR + 'shared/jansson.lib', buildsystem.DIST_LIB_SHARED_DIR)
        shutil.copy2(buildsystem.OUTPUT_DIR + 'shared/jansson.dll', buildsystem.DIST_LIB_SHARED_DIR)

        shutil.copy2(buildsystem.OUTPUT_DIR + 'static/jansson.lib', buildsystem.DIST_LIB_STATIC_DIR)

    else:     # Linux or MinGW or CygWin
        for file in glob.iglob(SOURCE_SRC_LIB_DIR + '*.a'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(SOURCE_SRC_LIB_DIR + '*.exp'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(SOURCE_SRC_LIB_DIR + '*.dll'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(SOURCE_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_STATIC_DIR)

        for file in glob.iglob(SOURCE_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_STATIC_DIR)


    artifactId = config["artifactId"]
    localfile = buildsystem.ARTIFACT_DIR + '/' + artifactId + '-' + str(aol)
    shutil.make_archive(localfile, buildsystem.PACKAGING, buildsystem.DIST_DIR)


####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    buildsystem.main(generate=generate, configure=configure, make=make, distribution=distribution)    
