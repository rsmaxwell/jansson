
import sys
import shutil
import buildsystem
import urllib.request
import gzip
import tarfile
import glob
import os
import subprocess
from os.path import expanduser


BUILD_SOURCE_MAIN_SRC_DIR     = './build/source/main/src/'
BUILD_SOURCE_MAIN_SRC_LIB_DIR = './build/source/main/src/lib/'


####################################################################################################
# Generate
####################################################################################################

def generate(config, aol):

    buildsystem.mkdir_p(buildsystem.BUILD_TEMP_DIR)

    srctargz = buildsystem.SRC_MAIN_ARCHIVE_DIR + 'jansson-2.9.tar.gz'

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(buildsystem.SRC_MAIN_ARCHIVE_DIR):
            os.makedirs(buildsystem.SRC_MAIN_ARCHIVE_DIR)

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = buildsystem.BUILD_TEMP_DIR + 'jansson-2.9.tar.gz'
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(buildsystem.BUILD_TEMP_DIR + 'jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(buildsystem.BUILD_TEMP_DIR + 'jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(buildsystem.BUILD_TEMP_DIR + 'jansson-2.9.tar')
    tar.extractall(buildsystem.BUILD_TEMP_DIR)
    tar.close()

    shutil.copytree(buildsystem.BUILD_TEMP_DIR + 'jansson-2.9', buildsystem.BUILD_SOURCE_MAIN_DIR)

    buildsystem.defaultGenerate(config, aol)


####################################################################################################
# Configure
####################################################################################################

def configure(config, aol):

    if aol.operatingSystem == 'windows':

        with open(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson_private_config.h', 'w') as f:
            f.write('#define HAVE_STDINT_H  1\n')

        filename = BUILD_SOURCE_MAIN_SRC_DIR + 'jansson_config.h'
        shutil.copy2(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson_config.h.in', filename)

        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin
        configureScript = 'configure'
        os.chmod(buildsystem.BUILD_SOURCE_MAIN_DIR + configureScript, 0o777)

        # Run the configure script
        p = subprocess.Popen(['bash', configureScript, '--prefix=/usr/local'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=buildsystem.BUILD_SOURCE_MAIN_DIR)
        buildsystem.checkProcessCompletesOk(config, p, 'Error: Configure failed')


####################################################################################################
# Make
####################################################################################################

def compile(config, aol):
    print('compile')

    buildsystem.mkdir_p(buildsystem.BUILD_OUTPUT_MAIN_DIR)

    if aol.operatingSystem == 'windows':
        makefile = os.path.relpath(buildsystem.SRC_MAIN_MAKE_DIR, buildsystem.BUILD_OUTPUT_MAIN_DIR) + '\\' + str(aol) + '.makefile'
        env = os.environ
        env['BUILD_TYPE'] = 'static'
        env['SOURCE'] = os.path.relpath(BUILD_SOURCE_MAIN_SRC_DIR, buildsystem.BUILD_OUTPUT_MAIN_DIR)
        env['OUTPUT'] = '.'
        env['INSTALL'] = buildsystem.INSTALL_DIR      

        args = ['make', '-f', makefile, 'clean', 'all']

        if buildsystem.verbose(config):
            print('Args = ' + str(args))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=buildsystem.BUILD_OUTPUT_MAIN_DIR)
        buildsystem.checkProcessCompletesOk(config, p, 'Error: Make failed', expectedReturnCodes=[0,1])


    else:     # Linux or MinGW or CygWin
        args = ['make', 'clean', 'all']

        if buildsystem.verbose(config):
            print('Args = ' + str(args))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=buildsystem.BUILD_SOURCE_MAIN_DIR)
        buildsystem.checkProcessCompletesOk(config, p, 'Error: Make failed', expectedReturnCodes=[0,1])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, aol):

    buildsystem.rmdir(buildsystem.DIST_DIR, buildsystem.DISTTEMP_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_DIR)

    buildsystem.mkdir_p(buildsystem.DIST_INCLUDE_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIB_SHARED_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIB_STATIC_DIR)
    buildsystem.mkdir_p(buildsystem.BUILD_ARTIFACT_DIR)

    shutil.copy2(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson.h', buildsystem.DIST_INCLUDE_DIR)
    shutil.copy2(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson_config.h', buildsystem.DIST_INCLUDE_DIR)

    if aol.operatingSystem == 'windows':
        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'shared/jansson.lib', buildsystem.DIST_LIB_SHARED_DIR)
        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'shared/jansson.dll', buildsystem.DIST_LIB_SHARED_DIR)

        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'static/jansson.lib', buildsystem.DIST_LIB_STATIC_DIR)

    else:     # Linux or MinGW or CygWin
        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.a'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.exp'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.dll'):
            shutil.copy2(file, buildsystem.DIST_LIB_SHARED_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_STATIC_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_STATIC_DIR)


    artifactId = config["artifactId"]
    localfile = buildsystem.BUILD_ARTIFACT_DIR + '/' + artifactId + '-' + str(aol)
    shutil.make_archive(localfile, buildsystem.PACKAGING, buildsystem.DIST_DIR)


####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    buildsystem.main(generate=generate, configure=configure, compile=compile, distribution=distribution)
