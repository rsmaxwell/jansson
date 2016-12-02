
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

def clean(config, dirs, aol, packaging):
    shutil.rmtree(dirs.build, ignore_errors=True)


####################################################################################################
# Generate
####################################################################################################

def generate(config, dirs, aol, packaging):

    if not os.path.exists(dirs.temp):
        os.makedirs(dirs.temp)

    srctargz = os.path.abspath(dirs.src + '/archive/' + 'jansson-2.9.tar.gz')

    if os.path.exists(srctargz):
        if buildsystem.verbose(config):
            print('Archive file already exists: ' + srctargz)
    else:
        if buildsystem.debug(config):
            print('Downloading ' + srctargz)

        if not os.path.exists(dirs.src + '/archive/'):
            os.makedirs(dirs.src + '/archive/')

        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, srctargz)

    temptargz = os.path.abspath(dirs.temp + '/' + 'jansson-2.9.tar.gz')
    shutil.copy2(srctargz, temptargz)

    inF = gzip.GzipFile(dirs.temp + '/jansson-2.9.tar.gz', 'rb')
    s = inF.read()
    inF.close()

    outF = open(dirs.temp + '/jansson-2.9.tar', 'wb')
    outF.write(s)
    outF.close()

    tar = tarfile.open(dirs.temp + '/jansson-2.9.tar')
    tar.extractall(dirs.temp)
    tar.close()

    shutil.copytree(dirs.temp + '/jansson-2.9', dirs.source)


####################################################################################################
# Configure
####################################################################################################

def configure(config, dirs, aol, packaging):

    location = os.path.join(dirs.output)
    if not os.path.exists(location):
        os.makedirs(location)


    location = dirs.dist
    if not os.path.exists(location):
        os.makedirs(location)

    if aol.operatingSystem == 'Windows':

        with open(dirs.sourcesrc + '/jansson_private_config.h', 'w') as text_file:
            print('#define HAVE_STDINT_H  1', file=text_file)

        filename = dirs.sourcesrc + '/jansson_config.h'
        shutil.copy2(dirs.sourcesrc + '/jansson_config.h.in', filename)
        buildsystem.inplace_change(filename, '@json_inline@', '__inline')
        buildsystem.inplace_change(filename, '@json_have_long_long@', '1')
        buildsystem.inplace_change(filename, '@json_have_localeconv@', '1')

    else:     # Linux or MinGW or CygWin

        script = os.path.join(dirs.source, 'configure')
        os.chmod(script, 0o777)

        buildsystem.runProgram(config, dirs.source, os.environ, ['bash', script, '--prefix=' + location])


####################################################################################################
# Make
####################################################################################################

def make(config, dirs, aol, packaging):

    if not os.path.exists(dirs.output):
        os.makedirs(dirs.output)

    if aol.operatingSystem == 'Windows':
        environ = os.environ
        environ['BUILD_TYPE'] = 'normal'
        environ['SOURCE'] = dirs.sourcesrc
        environ['OUTPUT'] = dirs.output
        buildsystem.runProgram(config, dirs.output, environ, ['make', '-f', src + '/make/' + aol.name + '.makefile', 'all'])

    else:     # Linux or MinGW or CygWin
        buildsystem.runProgram(config, dirs.source, os.environ, ['make', 'clean'])
        buildsystem.runProgram(config, dirs.source, os.environ, ['make'])
        buildsystem.runProgram(config, dirs.source, os.environ, ['make', 'install'])


####################################################################################################
# Dist
####################################################################################################

def distribution(config, dirs, aol, packaging):

        if aol.operatingSystem == 'Windows':

            shutil.rmtree(dirs.build + '/dist', ignore_errors=True)

            location = os.path.join(dirs.dist + '/headers')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(dirs.sourcesrc + '/jansson.h', dirs.dist + '/headers/jansson.h')
            shutil.copy2(dirs.sourcesrc + '/jansson_config.h', dirs.dist + '/headers/jansson_config.h')

            location = os.path.join(dirs.dist + '/libs/shared')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(dirs.output + '/shared/jansson.lib', dirs.dist + '/libs/shared/jansson.lib' )
            shutil.copy2(dirs.output + '/shared/jansson.dll', dirs.dist + '/libs/shared/jansson.dll' )

            location = os.path.join(dirs.dist + '/libs/static')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(dirs.output + '/static/jansson.lib', dirs.dist + '/libs/static/jansson.lib' )

#       else:     # Linux or MinGW or CygWin

        artifactDir = os.path.abspath(dirs.build + '/artifact')
        if not os.path.exists(artifactDir):
            os.makedirs(artifactDir)

        artifactId = config["artifactId"]
        localfile = os.path.abspath(artifactDir + '/' + artifactId + '-' + aol)
        packaging = 'zip'
        shutil.make_archive(localfile, packaging, dirs.build + '/dist')


####################################################################################################
# Deploy
####################################################################################################

def deploy(config, dirs, aol, packaging):

    groupId = config["groupId"]
    artifactId = config["artifactId"]
    version = buildsystem.multipleReplace(config["version"], config["properties"])
    packaging = 'zip'

    reposArtifactId = artifactId.replace('-', '/')
    reposArtifactId = reposArtifactId.replace('.', '-')

    mavenGroupId = groupId + '.' + reposArtifactId
    mavenArtifactId = artifactId + '-' + aol

    artifactDir = os.path.abspath(dirs.build + '/artifact')
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
