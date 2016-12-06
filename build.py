
import sys
import shutil
import buildsystem
import urllib.request
import gzip
import tarfile
import glob
import os
from os.path import expanduser


####################################################################################################
# Clean
####################################################################################################

def clean(config, location, aol, packaging):
    buildsystem.defaultClean(config, location, aol, packaging)


####################################################################################################
# Generate
####################################################################################################

def generate(config, location, aol, packaging):

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

def configure(config, location, aol, packaging):

    buildsystem.mkdir_p(buildsystem.DIST_DIR)

    if aol.operatingSystem == 'windows':

        with open(buildsystem.SOURCESRC_DIR + 'jansson_private_config.h', 'w') as f:
            f.write('#define HAVE_STDINT_H  1\n')

        filename = buildsystem.SOURCESRC_DIR + 'jansson_config.h'
        shutil.copy2(buildsystem.SOURCESRC_DIR + 'jansson_config.h.in', filename)
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

def make(config, location, aol, packaging):

    buildsystem.mkdir_p(buildsystem.OUTPUT_DIR)

    if aol.operatingSystem == 'windows':
        makefile = os.path.relpath(buildsystem.MAKE_DIR, buildsystem.OUTPUT_DIR) + '\\' + str(aol) + '.makefile'

        environ = os.environ
        environ['BUILD_TYPE'] = 'normal'
        environ['SOURCE'] = os.path.relpath(buildsystem.SOURCESRC_DIR, buildsystem.OUTPUT_DIR)
        environ['OUTPUT'] = '.'
        buildsystem.runProgram(config, buildsystem.OUTPUT_DIR, os.environ, ['make', '-f', makefile, 'clean', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, buildsystem.SOURCE_DIR, os.environ, ['make', 'clean', 'all'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, location, aol, packaging):

    buildsystem.rmdir(buildsystem.DIST_DIR, buildsystem.DISTTEMP_DIR)
    os.makedirs(distDir)

    buildsystem.mkdir_p(buildsystem.DIST_HEADERS_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIBS_SHARED_DIR)
    buildsystem.mkdir_p(buildsystem.DIST_LIBS_STATIC_DIR)
    buildsystem.mkdir_p(buildsystem.ARTIFACT_DIR)


    if aol.operatingSystem == 'windows':
        shutil.copy2(buildsystem.SOURCE_DIR + 'jansson.h', buildsystem.DIST_HEADERS_DIR + 'jansson.h')
        shutil.copy2(buildsystem.SOURCESRC_DIR + 'jansson_config.h', buildsystem.DIST_HEADERS_DIR + 'jansson_config.h')

        shutil.copy2(buildsystem.OUTPUT_DIR + 'shared/jansson.lib', buildsystem.DIST_LIBS_SHARED_DIR + 'jansson.lib' )
        shutil.copy2(buildsystem.OUTPUT_DIR + 'shared/jansson.dll', buildsystem.DIST_LIBS_SHARED_DIR + 'jansson.dll' )

        shutil.copy2(buildsystem.OUTPUT_DIR + 'static/jansson.lib', buildsystem.DIST_LIBS_STATIC_DIR + 'jansson.lib' )

    else:     # Linux or MinGW or CygWin
        files = glob.iglob(buildsystem.SOURCESRCLIB_DIR + '*.a')
        for file in files:
            shutil.copy2(file, sharedDir + os.path.basename(file))

        files = glob.iglob(buildsystem.SOURCESRCLIB_DIR + '*.exp')
        for file in files:
            shutil.copy2(file, buildsystem.DIST_LIBS_SHARED_DIR + os.path.basename(file))

        files = glob.iglob(buildsystem.SOURCESRCLIB_DIR + '*.dll')
        for file in files:
            shutil.copy2(file, sharedDir + os.path.basename(file))

        files = glob.iglob(buildsystem.SOURCESRCLIB_DIR + '*.la*')
        for file in files:
            shutil.copy2(file, buildsystem.DIST_LIBS_STATIC_DIR + os.path.basename(file))

        shutil.copy2(buildsystem.SOURCESRC_DIR + 'jansson.h', buildsystem.DIST_HEADERS_DIR + 'jansson.h')



    artifactId = config["artifactId"]
    localfile = buildsystem.ARTIFACT_DIR + '/' + artifactId + '-' + str(aol)
    shutil.make_archive(localfile, packaging, distDir)


####################################################################################################
# Deploy
####################################################################################################

def deploy(config, location, aol, packaging):

    groupId = config["groupId"]
    artifactId = config["artifactId"]
    version = buildsystem.multipleReplace(config["version"], config["properties"])

    reposArtifactId = artifactId.replace('-', '/')
    reposArtifactId = reposArtifactId.replace('.', '-')

    mavenGroupId = groupId + '.' + reposArtifactId
    mavenArtifactId = artifactId + '-' + str(aol)

    filename = os.path.abspath(buildsystem.ARTIFACT_DIR + mavenArtifactId + '.' + packaging)

    if buildsystem.debug(config):
        print('main: deploy')
        print('    groupId = ' + groupId)
        print('    artifactId = ' + artifactId)
        print('    mavenGroupId = ' + mavenGroupId)
        print('    mavenArtifactId = ' + mavenArtifactId)
        print('    aol = ' + str(aol))
        print('    version = ' + version)
        print('    packaging = ' + packaging)
        print('    filename = ' + filename)

    buildsystem.uploadArtifact(config, mavenGroupId, mavenArtifactId, version, packaging, filename)



####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    buildsystem.main(sys.argv, clean, generate, configure, make, distribution, deploy)
