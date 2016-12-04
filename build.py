
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

    sourceDir = location.build + location.source
    archiveDir = location.src + location.archive
    tempDir = location.build + location.temp

    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    srctargz = archiveDir + 'jansson-2.9.tar.gz'

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(archiveDir):
            os.makedirs(archiveDir)

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = tempDir + 'jansson-2.9.tar.gz'
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(tempDir + 'jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(tempDir + 'jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(tempDir + 'jansson-2.9.tar')
    tar.extractall(tempDir)
    tar.close()

    shutil.copytree(tempDir + 'jansson-2.9', sourceDir)


####################################################################################################
# Configure
####################################################################################################

def configure(config, location, aol, packaging):

    buildDir = location.build
    sourceDir = location.build + location.source
    sourceSrcDir = location.build + location.source + location.src
    outputDir = location.build + location.output
    distDir = location.build + location.dist

    buildsystem.mkdir_p(outputDir) 
    buildsystem.mkdir_p(distDir) 

    if aol.operatingSystem == 'Windows':

        with open(sourceSrcDir + 'jansson_private_config.h', 'w') as f:
            f.write('#define HAVE_STDINT_H  1\n')

        filename = sourceSrcDir + 'jansson_config.h'
        shutil.copy2(sourceSrcDir + 'jansson_config.h.in', filename)
        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin

        configureScript = 'configure'
        os.chmod(sourceDir + configureScript, 0o777)

        buildsystem.runProgram(config, sourceDir, os.environ, ['bash', configureScript, '--prefix=/usr/local'])


####################################################################################################
# Make
####################################################################################################

def make(config, location, aol, packaging):

    sourceDir = location.build + location.source
    sourceSrcDir = location.build + location.source + location.src

    if aol.operatingSystem == 'Windows':
        outputDir = location.build + location.output
        buildsystem.mkdir_p(outputDir)

        environ = os.environ
        environ['BUILD_TYPE'] = 'normal'
        environ['SOURCE'] = sourceSrcDir
        environ['OUTPUT'] = outputDir
        buildsystem.runProgram(config, outputDir, os.environ, ['make', '-f', sourceSrcDir + '/make/' + str(aol) + '.makefile', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, sourceDir, os.environ, ['make', 'clean'])
        buildsystem.runProgram(config, sourceDir, os.environ, ['make'])
        buildsystem.runProgram(config, sourceDir, os.environ, ['make', 'install'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, location, aol, packaging):

    sourceDir = location.build + location.source
    sourceSrcDir = location.build + location.source + location.sourcesrc
    sourceSrcLibDir = location.build + location.source + location.sourcesrc + '.libs/'
    artifactDir = location.build + location.artifact
    buildsystem.mkdir_p(artifactDir)

    outputDir = location.build + location.output
    distDir = location.build + location.dist
    distTempDir = location.build + location.distTemp
    buildsystem.rmdir(distDir, distTempDir)
    os.makedirs(distDir)

    sharedDir = location.build + location.dist + 'libs/shared/'
    buildsystem.mkdir_p(sharedDir)

    staticDir = location.build + location.dist + 'libs/static/'
    buildsystem.mkdir_p(staticDir)

    headersDir = location.build + location.dist + 'headers/'
    buildsystem.mkdir_p(headersDir)

    if aol.operatingSystem == 'Windows':
        shutil.copy2(sourceSrcDir + 'jansson.h', headersDir + 'jansson.h')
        shutil.copy2(sourceSrcDir + 'jansson_config.h', headersDir + 'jansson_config.h')

        shutil.copy2(outputDir + 'shared/jansson.lib', sharedDir + 'jansson.lib' )
        shutil.copy2(outputDir + 'shared/jansson.dll', sharedDir + 'jansson.dll' )

        shutil.copy2(outputDir + 'static/jansson.lib', staticDir + 'jansson.lib' )

    else:     # Linux or MinGW or CygWin
        files = glob.iglob(sourceSrcLibDir + '*.a')
        for file in files:
            shutil.copy2(file, sharedDir + os.path.basename(file))

        files = glob.iglob(sourceSrcLibDir + '*.exp')
        for file in files:
            shutil.copy2(file, sharedDir + os.path.basename(file))

        files = glob.iglob(sourceSrcLibDir + '*.dll')
        for file in files:
            shutil.copy2(file, sharedDir + os.path.basename(file))

        files = glob.iglob(sourceSrcLibDir + '*.la*')
        for file in files:
            shutil.copy2(file, staticDir + os.path.basename(file))

        shutil.copy2(sourceSrcDir + 'jansson.h', headersDir + 'jansson.h')        



    artifactId = config["artifactId"]
    localfile = artifactDir + '/' + artifactId + '-' + str(aol)
    shutil.make_archive(localfile, packaging, distDir)


####################################################################################################
# Deploy
####################################################################################################

def deploy(config, location, aol, packaging):

    artifactDir = location.build + location.artifact

    groupId = config["groupId"]
    artifactId = config["artifactId"]
    version = buildsystem.multipleReplace(config["version"], config["properties"])

    reposArtifactId = artifactId.replace('-', '/')
    reposArtifactId = reposArtifactId.replace('.', '-')

    mavenGroupId = groupId + '.' + reposArtifactId
    mavenArtifactId = artifactId + '-' + str(aol)

    filename = os.path.abspath(artifactDir + mavenArtifactId + '.' + packaging)

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
