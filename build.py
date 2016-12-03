
import sys
import shutil
import buildsystem
import urllib.request
import gzip
import tarfile
import os
from os.path import expanduser


####################################################################################################
# Clean
####################################################################################################

def clean(config, location, aol, packaging):
    shutil.rmtree(location.build, ignore_errors=True)


####################################################################################################
# Generate
####################################################################################################

def generate(config, location, aol, packaging):

    if not os.path.exists(location.temp):
        os.makedirs(location.temp)

    srctargz = os.path.abspath(location.src + '/archive/' + 'jansson-2.9.tar.gz')

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(location.src + '/archive/'):
            os.makedirs(location.src + '/archive/')

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = os.path.abspath(location.temp + '/' + 'jansson-2.9.tar.gz')
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(location.temp + '/jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(location.temp + '/jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(location.temp + '/jansson-2.9.tar')
    tar.extractall(location.temp)
    tar.close()

    shutil.copytree(location.temp + '/jansson-2.9', location.source)


####################################################################################################
# Configure
####################################################################################################

def configure(config, location, aol, packaging):

    if not os.path.exists(location.output):
        os.makedirs(location.output)

    if not os.path.exists(location.dist):
        os.makedirs(location.dist)

    if aol.operatingSystem == 'Windows':

        with open(location.sourcesrc + '/jansson_private_config.h', 'w') as text_file:
            print('#define HAVE_STDINT_H  1', file=text_file)

        filename = location.sourcesrc + '/jansson_config.h'
        shutil.copy2(location.sourcesrc + '/jansson_config.h.in', filename)
        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin

        script = os.path.join(location.source, 'configure')
        os.chmod(script, 0o777)

        buildsystem.runProgram(config, location.source, os.environ, ['bash', script, '--prefix=' + location.dist])


####################################################################################################
# Make
####################################################################################################

def make(config, location, aol, packaging):

    if not os.path.exists(location.output):
        os.makedirs(location.output)

    if aol.operatingSystem == 'Windows':
        environ = os.environ
        environ['BUILD_TYPE'] = 'normal'
        environ['SOURCE'] = location.sourcesrc
        environ['OUTPUT'] = location.output
        buildsystem.runProgram(config, location.output, environ, ['make', '-f', location.src + '/make/' + str(aol) + '.makefile', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, location.source, os.environ, ['make', 'clean'])
        buildsystem.runProgram(config, location.source, os.environ, ['make'])
        buildsystem.runProgram(config, location.source, os.environ, ['make', 'install'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, location, aol, packaging):

        if aol.operatingSystem == 'Windows':

            shutil.rmtree(location.build + '/dist', ignore_errors=True)

            headers = os.path.join(location.dist + '/headers')
            if not os.path.exists(headers):
                os.makedirs(headers)

            shutil.copy2(location.sourcesrc + '/jansson.h', location.dist + '/headers/jansson.h')
            shutil.copy2(location.sourcesrc + '/jansson_config.h', location.dist + '/headers/jansson_config.h')

            shared = os.path.join(location.dist + '/libs/shared')
            if not os.path.exists(shared):
                os.makedirs(shared)

            shutil.copy2(location.output + '/shared/jansson.lib', location.dist + '/libs/shared/jansson.lib' )
            shutil.copy2(location.output + '/shared/jansson.dll', location.dist + '/libs/shared/jansson.dll' )

            static = os.path.join(location.dist + '/libs/static')
            if not os.path.exists(static):
                os.makedirs(static)

            shutil.copy2(location.output + '/static/jansson.lib', location.dist + '/libs/static/jansson.lib' )

#       else:     # Linux or MinGW or CygWin

        artifactDir = os.path.abspath(location.build + '/artifact')
        if not os.path.exists(artifactDir):
            os.makedirs(artifactDir)

        artifactId = config["artifactId"]
        localfile = os.path.abspath(artifactDir + '/' + artifactId + '-' + str(aol))
        packaging = 'zip'
        shutil.make_archive(localfile, packaging, location.build + '/dist')


####################################################################################################
# Deploy
####################################################################################################

def deploy(config, location, aol, packaging):

    groupId = config["groupId"]
    artifactId = config["artifactId"]
    version = buildsystem.multipleReplace(config["version"], config["properties"])
    packaging = 'zip'

    reposArtifactId = artifactId.replace('-', '/')
    reposArtifactId = reposArtifactId.replace('.', '-')

    mavenGroupId = groupId + '.' + reposArtifactId
    mavenArtifactId = artifactId + '-' + aol

    artifactDir = os.path.abspath(location.build + '/artifact')
    filename = os.path.abspath(artifactDir + '/' + mavenArtifactId + '.' + packaging)

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
