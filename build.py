
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
BUILD_SOURCE_MAIN_SRC_LIB_DIR = './build/source/main/src/.libs/'


####################################################################################################
# Generate
####################################################################################################

def generate(config, aol):

    buildsystem.mkdir(config, aol, buildsystem.BUILD_TEMP_DIR)

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
        if (buildsystem.verbose(config)):
            print('Working Directory = ' + buildsystem.BUILD_SOURCE_MAIN_DIR)

        args = ['bash', configureScript, '--prefix=/usr/local']

        if buildsystem.verbose(config):
            print('Args = ' + str(args))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=buildsystem.BUILD_SOURCE_MAIN_DIR)
        stdout, stderr = p.communicate()
        returncode = p.wait()

        if (returncode != 0):
            print('Error: test ' + file + ' failed')

        if (returncode != 0) or (buildsystem.verbose(config)):
            print('---------[ stdout ]-----------------------------------------------------------------')
            print(stdout.decode('utf-8'))
            print('---------[ stderr ]-----------------------------------------------------------------')
            print(stderr.decode('utf-8'))
            print('---------[ returncode = ' + str(returncode) + ']--------------------------------------------------------')

        if (returncode != 0):
            sys.exit(1)




####################################################################################################
# Compile
####################################################################################################

def compile(config, aol):
    print('compile')

    buildsystem.mkdir(config, aol, buildsystem.BUILD_OUTPUT_MAIN_DIR)

    buildsystem.writeCompileTimeMetadata(config, aol)

    if aol.operatingSystem == 'windows':
        makefile = os.path.relpath(buildsystem.SRC_MAIN_MAKE_DIR, buildsystem.BUILD_OUTPUT_MAIN_DIR) + '\\' + str(aol) + '.makefile'
        source = os.path.relpath(BUILD_SOURCE_MAIN_SRC_DIR, buildsystem.BUILD_OUTPUT_TEST_DIR)
        dist = os.path.relpath(buildsystem.DIST_DIR, buildsystem.BUILD_OUTPUT_MAIN_DIR)

        env = os.environ
        env['BUILD_TYPE'] = 'static'
        env['SOURCE'] = source
        env['DIST'] = dist
        env['INSTALL'] = buildsystem.INSTALL_DIR      

        args = ['make', '-f', makefile, 'clean', 'install']

        if buildsystem.verbose(config):
            print('Args = ' + str(args))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=buildsystem.BUILD_OUTPUT_MAIN_DIR)
        buildsystem.checkProcessCompletesOk(config, p, 'Error: Make failed', expectedReturnCodes=[0,1])


    else:     # Linux or MinGW or CygWin

        workingDir = buildsystem.BUILD_SOURCE_MAIN_DIR

        if (buildsystem.verbose(config)):
            print('Working Directory = ' + workingDir)

        args = ['make']

        if buildsystem.verbose(config):
            print('Args = ' + str(args))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workingDir)
        stdout, stderr = p.communicate()
        returncode = p.wait()

        if (returncode != 0):
            print('Error: test ' + file + ' failed')

        if (returncode != 0) or (buildsystem.verbose(config)):
            print('---------[ stdout ]-----------------------------------------------------------------')
            print(stdout.decode('utf-8'))
            print('---------[ stderr ]-----------------------------------------------------------------')
            print(stderr.decode('utf-8'))
            print('---------[ returncode = ' + str(returncode) + ']--------------------------------------------------------')

        if (returncode != 0):
            sys.exit(1)





#       workingDir = buildsystem.BUILD_SOURCE_MAIN_DIR
#
#       if (buildsystem.verbose(config)):
#           print('Working Directory = ' + workingDir)
#
#       args = ['make', 'check']
#
#       if buildsystem.verbose(config):
#           print('Args = ' + str(args))
#
#       p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workingDir)
#       stdout, stderr = p.communicate()
#       returncode = p.wait()
#
#       if (returncode != 0):
#           print('Error: test ' + file + ' failed')
#
#       if (returncode != 0) or (buildsystem.verbose(config)):
#           print('---------[ stdout ]-----------------------------------------------------------------')
#           print(stdout.decode('utf-8'))
#           print('---------[ stderr ]-----------------------------------------------------------------')
#           print(stderr.decode('utf-8'))
#           print('---------[ returncode = ' + str(returncode) + ']--------------------------------------------------------')
#
#       if (returncode != 0):
#           sys.exit(1)









####################################################################################################
# Dist
####################################################################################################

def distribution(config, aol):

    buildsystem.mkdir(config, aol, buildsystem.DIST_DIR)

    buildsystem.mkdir(config, aol, buildsystem.DIST_INCLUDE_DIR)
    buildsystem.mkdir(config, aol, buildsystem.DIST_LIB_DIR)
    buildsystem.mkdir(config, aol, buildsystem.BUILD_ARTIFACT_DIR)

    shutil.copy2(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson.h', buildsystem.DIST_INCLUDE_DIR)
    shutil.copy2(BUILD_SOURCE_MAIN_SRC_DIR + 'jansson_config.h', buildsystem.DIST_INCLUDE_DIR)

    if aol.operatingSystem == 'windows':
        buildsystem.mkdir(config, aol, buildsystem.DIST_LIB_SHARED_DIR)
        buildsystem.mkdir(config, aol, buildsystem.DIST_LIB_STATIC_DIR + 'exe/')

        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'shared/jansson.lib', buildsystem.DIST_LIB_SHARED_DIR)
        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'shared/jansson.dll', buildsystem.DIST_LIB_SHARED_DIR)

        shutil.copy2(buildsystem.BUILD_OUTPUT_MAIN_DIR + 'static/jansson.lib', buildsystem.DIST_LIB_STATIC_DIR + 'exe/')

    else:     # Linux or MinGW or CygWin
        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.a'):
            shutil.copy2(file, buildsystem.DIST_LIB_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.exp'):
            shutil.copy2(file, buildsystem.DIST_LIB_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.dll'):
            shutil.copy2(file, buildsystem.DIST_LIB_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_DIR)

        for file in glob.iglob(BUILD_SOURCE_MAIN_SRC_LIB_DIR + '*.la*'):
            shutil.copy2(file, buildsystem.DIST_LIB_DIR)



####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    buildsystem.main(generate=generate, configure=configure, compile=compile, distribution=distribution)
