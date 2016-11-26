
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

def clean(config, build):
    shutil.rmtree(build, ignore_errors=True)


####################################################################################################
# Generate
####################################################################################################

def generate(config, src, source, temp, os, operatingSystem, aol, packaging, dependances):

    if not os.path.exists(temp):
        os.makedirs(temp)

    srctargz = os.path.abspath(src + '/archive/' + 'jansson-2.9.tar.gz')

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(src + '/archive/'):
            os.makedirs(src + '/archive/')

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = os.path.abspath(temp + '/' + 'jansson-2.9.tar.gz')
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(temp + '/jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(temp + '/jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(temp + '/jansson-2.9.tar')
    tar.extractall(temp)
    tar.close()

    shutil.copytree(temp + '/jansson-2.9', source)


####################################################################################################
# Configure
####################################################################################################

def configure(config, output, source, dist, operatingSystem, sourcesrc):

    location = os.path.join(output)
    if not os.path.exists(location):
        os.makedirs(location)


    location = dist
    if not os.path.exists(location):
        os.makedirs(location)

    if operatingSystem == 'Windows':

        with open(sourcesrc + '/jansson_private_config.h', 'w') as text_file:
            print('#include <stdint.h>', file=text_file)

        filename = sourcesrc + '/jansson_config.h'
        shutil.copy2(sourcesrc + '/jansson_config.h.in', filename)
        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin

        script = os.path.join(source, 'configure')
        os.chmod(script, 0o777)

        buildsystem.runProgram(config, source, os.environ, ['bash', script, '--prefix=' + location])


####################################################################################################
# Make
####################################################################################################

def make(config, src, source, sourcesrc, output, build, os, operatingSystem, aol):

    if operatingSystem == 'Windows':
        environ = os.environ
        environ['BUILD_TYPE'] = 'normal'
        environ['SOURCE'] = sourcesrc
        environ['OUTPUT'] = output
        buildsystem.runProgram(config, output, environ, ['make', '-f', src + '/make/' + aol + '.makefile', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, source, os.environ, ['make', 'clean'])
        buildsystem.runProgram(config, source, os.environ, ['make'])
        buildsystem.runProgram(config, source, os.environ, ['make', 'install'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, build, dist, os, operatingSystem, aol, packaging):

        if operatingSystem == 'Windows':

            shutil.rmtree(build + '/dist', ignore_errors=True)

            location = os.path.join(dist + '/headers')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(sourcesrc + '/jansson.h', dist + '/headers/jansson.h')
            shutil.copy2(sourcesrc + '/jansson_config.h', dist + '/headers/jansson_config.h')

            location = os.path.join(dist + '/libs/shared')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(output + '/shared/jansson.lib', dist + '/libs/shared/jansson.lib' )
            shutil.copy2(output + '/shared/jansson.dll', dist + '/libs/shared/jansson.dll' )

            location = os.path.join(dist + '/libs/static')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(output + '/static/jansson.lib', dist + '/libs/static/jansson.lib' )

#       else:     # Linux or MinGW or CygWin

        artifactDir = os.path.abspath(build + '/artifact')
        if not os.path.exists(artifactDir):
            os.makedirs(artifactDir)

        artifactId = config["artifactId"]
        localfile = os.path.abspath(artifactDir + '/' + artifactId + '-' + aol)
        packaging = 'zip'
        shutil.make_archive(localfile, packaging, build + '/dist')


####################################################################################################
# Deploy
####################################################################################################

def deploy(config, build, os, aol, packaging):

    groupId = config["groupId"]
    artifactId = config["artifactId"]
    version = buildsystem.multipleReplace(config["version"], config["properties"])
    packaging = 'zip'

    reposArtifactId = artifactId.replace('-', '/')
    reposArtifactId = reposArtifactId.replace('.', '-')

    mavenGroupId = groupId + '.' + reposArtifactId
    mavenArtifactId = artifactId + '-' + aol

    artifactDir = os.path.abspath(build + '/artifact')
    filename = os.path.abspath(artifactDir + '/' + mavenArtifactId + '.' + packaging)

    if buildsystem.debug(config):
        print('main: deploy')
        print('    groupId = ' + groupId)
        print('    artifactId = ' + artifactId)
        print('    mavenGroupId = ' + mavenGroupId)
        print('    mavenArtifactId = ' + mavenArtifactId)
        print('    aol = ' + aol)
        print('    version = ' + version)
        print('    packaging = ' + packaging)
        print('    filename = ' + filename)

    buildsystem.uploadArtifact(config, mavenGroupId, mavenArtifactId, version, packaging, filename)



####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    buildsystem.main(sys.argv, clean, generate, configure, make, distribution, deploy)
