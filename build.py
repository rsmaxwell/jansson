

import platform
import os
import subprocess
import sys
import shutil
import gzip
import tarfile
import re
import argparse
import glob
import requests
import io
import datetime
import hashlib
from io import BytesIO
import xml.etree.ElementTree as ET
import urllib.request

architecture = 'undefined'
operatingSystem = 'undefined'
linker = 'undefined'
aol = 'undefined'

verbose=False
version='SNAPSHOT'


####################################################################################################
# Calculate MD5 hash of a file
####################################################################################################

def md5(file):
    hash_md5 = hashlib.md5()
    file.seek(0, os.SEEK_SET)
    for chunk in iter(lambda: file.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


####################################################################################################
# Calculate SHA1 hash of a file
####################################################################################################

def sha1(file):
    hash_sha1 = hashlib.sha1()
    file.seek(0, os.SEEK_SET)
    for chunk in iter(lambda: file.read(4096), b""):
        hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


####################################################################################################
# Find a program on the PATH
####################################################################################################

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


####################################################################################################
# inplace_change
####################################################################################################

def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            # print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        # print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)


####################################################################################################
# Run a program and wait for the result
####################################################################################################

def runProgram (arguments, workingDirectory, environment):

    if verbose:
        print('------------------------------------------------------------------------------------')
        print('subprocess:', arguments)
        #print('environment:', environment)

    p = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, cwd=workingDirectory)
    stdout = p.stdout.read().decode('utf-8')
    stderr = p.stderr.read().decode('utf-8')
    returncode = p.returncode

    if verbose:
        print('---------[ stdout ]-----------------------------------------------------------------')
        print(stdout)
        print('---------[ stderr ]-----------------------------------------------------------------')
        print(stderr)
        print('---------[ exitCode ]---------------------------------------------------------------')
        print(returncode)
        print('------------------------------------------------------------------------------------')

    return stdout, stderr, returncode



####################################################################################################
# Parse the version from the metadata
####################################################################################################

def parseReleaseNumberFromMetadata(content):

    if verbose:
        print("parseReleaseNumberFromMetadata")

    root = ET.fromstring(content)

    versioning = root.find('versioning')
    if versioning == None:
        print('Error parsing metadata: Could not find the \'versioning\' tag')
        print('content:')
        print(content)
        sys.exit(3)

    release = versioning.find('release')
    if release == None:
        print('Error parsing metadata: Could not find the \'release\' tag')
        print('content:')
        print(content)
        sys.exit(5)

    if verbose:
        print('    release =', release.text)

    return release.text


####################################################################################################
# Parse the build number from the metadata
####################################################################################################

def parseBuildNumberFromMetadata(content):

    if verbose:
        print("parseBuildNumberFromMetadata")

    root = ET.fromstring(content)

    versioning = root.find('versioning')
    if versioning == None:
        print('Error parsing metadata: Could not find the \'versioning\' tag')
        print('content:')
        print(content)
        sys.exit(3)

    snapshot = versioning.find('snapshot')
    if snapshot == None:
        print('Error parsing metadata: Could not find the \'snapshot\' tag')
        print('content:')
        print(content)
        sys.exit(4)

    buildNumber = snapshot.find('buildNumber')
    if buildNumber == None:
        print('Error parsing metadata: Could not find the \'buildNumber\' tag')
        print('content:')
        print(content)
        sys.exit(5)

    if verbose:
        print('    buildNumber =', buildNumber.text)

    return int(buildNumber.text)



####################################################################################################
# Read the metadata and return the version
####################################################################################################

def getReleaseNumberFromMetadata(baseUrl, groupId, artifactId):

    metadataUrl = baseUrl + '/' + groupId.replace('.', '/') + '/' + artifactId + '/' + 'maven-metadata.xml'

    # Get the metadata to discover the current build number
    r = requests.get(metadataUrl, stream=True)

    # Upload the given file
    if r.status_code == 200: # http.HTTPStatus.OK.value
        if verbose:
            print('getVersionFromMetadata')
            print('    Artifact was found in Nexus')

        releaseNumber = parseReleaseNumberFromMetadata(r.text)


    elif r.status_code == 404: # http.HTTPStatus.NOT_FOUND.value
        if verbose:
            print('getVersionFromMetadata')
            print('    Artifact not found in Nexus')
        releaseNumber = '0'


    else:
        print('Unexpected Http response ' + str(r.status_code) + ' when getting: maven-metadata.xml')
        print('    metadataUrl: ' + metadataUrl)
        content = r.raw.decode('utf-8')
        print('Content =', content)
        sys.exit(99)

    if verbose:
        print('getReleaseNumberFromMetadata')
        print('    releaseNumber = ' + releaseNumber)

    return releaseNumber

####################################################################################################
# Read the metadata and return the version
####################################################################################################

def getBuildNumberFromMetadata(baseUrl, groupId, artifactId):

    metadataUrl = baseUrl + '/' + groupId.replace('.', '/') + '/' + artifactId + '/' + 'SNAPSHOT' + '/' + 'maven-metadata.xml'

    # Get the metadata to discover the current build number
    r = requests.get(metadataUrl, stream=True)

    # Upload the given file
    if r.status_code == 200: # http.HTTPStatus.OK.value
        if verbose:
            print('getBuildNumberFromMetadata')
            print('    Artifact was found in Nexus')

        buildNumber = 1 + parseBuildNumberFromMetadata(r.text)


    elif r.status_code == 404: # http.HTTPStatus.NOT_FOUND.value
        if verbose:
            print('getBuildNumberFromMetadata')
            print('    Artifact not found in Nexus')
        buildNumber = 1


    else:
        print('Unexpected Http response ' + str(r.status_code) + ' when getting: maven-metadata.xml')
        print('    metadataUrl: ' + metadataUrl)
        content = r.raw.decode('utf-8')
        print('Content =', content)
        sys.exit(99)

    print('buildNumber = ' + str(buildNumber))
    return str(buildNumber)



####################################################################################################
# Utility methods to make usefull endpoints
####################################################################################################

def makeArtifactEndpoint(host, repository):
    return 'http://' + host + '/nexus/service/local/repositories/' + repository + '/content'


def makeServiceEndpoint(host, repository):
    return 'http://' + host + '/nexus/service/local/metadata/repositories/' + repository + '/content'


def makeMetadataUrl(endpoint, groupId, artifactId):
    pathname = groupId.replace('.', '/') + '/' + artifactId
    return endpoint + '/' + pathname


def makeReleaseFileUrl(endpoint, groupId, artifactId, version):
    pathname = groupId.replace('.', '/') + '/' + artifactId + '/' + str(version)
    filename = artifactId
    return endpoint + '/' + pathname + '/' + filename

def makeSnapshotFileUrl(endpoint, groupId, artifactId):
    timestamp = '{:%Y%m%d.%H%M%S}'.format(datetime.datetime.now())
    buildNumber = getBuildNumberFromMetadata(endpoint, groupId, artifactId)
    pathname = groupId.replace('.', '/') + '/' + artifactId + '/' + 'SNAPSHOT'
    filename = artifactId + '-' + timestamp + '-' + buildNumber
    return endpoint + '/' + pathname + '/' + filename


####################################################################################################
# Delete a URL resource
#
# Make the Nexus repository rebuild its metadata
# curl -v --request DELETE  --user "login:password"  --silent http://nexusHost/service/local/metadata/repositories/myRepository/content
#
####################################################################################################

def rebuildMetadata(url):

    if verbose:
        print('rebuildMetadata')
        print('    url =', url)

    USER=os.environ["MAXWELLHOUSE_ADMIN_USER"]
    PASSWORD=os.environ["MAXWELLHOUSE_ADMIN_PASS"]

    r = requests.delete(url, auth=(USER, PASSWORD))
    statusCode = r.status_code

    if verbose:
        print('rebuildMetadata')
        print('    url =', url)
        print('    statusCode =', statusCode)

    return statusCode


####################################################################################################
# Download a URL into a buffer
####################################################################################################

def download(url):

    r = requests.get(url, stream=True)

    statusCode = r.status_code

    if statusCode != 200: # http.HTTPStatus.OK.value
        print('Error download content: statusCode = ', statusCode)
        sys.exit(5)

    buffer.write(BytesIO(r.content))

    if verbose:
        print('download')
        print('    url =', url)
        print('    statusCode =', statusCode)

    return r


####################################################################################################
# Upload a stream to a URL
####################################################################################################

def uploadFile(file, url):

    if verbose:
        print('uploadFile')
        print('    url =', url)

    USER=os.environ["MAXWELLHOUSE_ADMIN_USER"]
    PASSWORD=os.environ["MAXWELLHOUSE_ADMIN_PASS"]

    file.seek(0, os.SEEK_END)
    fileSize = file.tell()

    file.seek(0, os.SEEK_SET)

    files = {'file': file}
    r = requests.post(url, files=files, auth=(USER, PASSWORD))

    statusCode = r.status_code

    if statusCode != 201: # http.HTTPStatus.CREATED.value
        print('Error uploading content: statusCode = ', statusCode)
        sys.exit(5)

    if verbose:
        print('uploadFile')
        print('    url =', url)
        print('    statusCode =', statusCode)

    return statusCode


####################################################################################################
# Upload a string
####################################################################################################

def uploadString(string, url):

    if verbose:
        print("uploadString")
        print("    string =", string)
        print("    url =", url)

    file = io.StringIO(string)
    uploadFile(file, url)
    file.close()


####################################################################################################
# Upload a file and its metadata to Artifact
####################################################################################################

def uploadFileAndHashes(file, url):

    if verbose:
        print("uploadFileAndHashes")
        print("    url =", url)

    uploadFile(file, url)
    uploadString(md5(file), url + '.md5')
    uploadString(sha1(file), url + '.sha1')


####################################################################################################
# Make POM
####################################################################################################

def makePom(groupId, artifactId, version, packaging):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    lines.append('<project xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns="http://maven.apache.org/POM/4.0.0"\n')
    lines.append('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
    lines.append('  <modelVersion>4.0.0</modelVersion>\n')
    lines.append('  <groupId>' + groupId + '</groupId>\n')
    lines.append('  <artifactId>' + artifactId + '</artifactId>\n')
    lines.append('  <version>' + version + '</version>\n')
    lines.append('  <packaging>' + packaging + '</packaging>\n')
    lines.append('</project>\n')

    buffer = BytesIO()
    for line in lines:
        buffer.write(line.encode('utf-8'))
    return buffer

####################################################################################################
# Upload a file and its md5 and its sha1 to Nexus
####################################################################################################

def generateNextVersion(releaseNumber):

    if verbose:
        print('generateNextVersion')
        print('    releaseNumber =', releaseNumber)

    # Split the releaseNumber into dot separated string
    words = releaseNumber.split('.')
    length = len(words)
    lastWord = words[length - 1]

    try:
        newLastWord = str(int(lastWord) + 1)
    except ValueError:
        print('Cannot increment the releaseNumber = ' + releaseNumber)
        print('lastWord = ' + lastWord)
        sys.exit(3)

    if verbose:
        print('    newLastWord =', newLastWord)

    words[length - 1] = str(newLastWord)
    version = '.'.join(words)

    if verbose:
        print('    version =', version)

    return version;

####################################################################################################
# Upload a file and its md5 and its sha1 to Nexus
####################################################################################################

def uploadArtifact(host, repository, groupId, artifactId, packaging, localfile):

    global version

    if verbose:
        print('uploadArtifact')
        print('    host =', host)
        print('    repository =', repository)
        print('    artifactId =', artifactId)
        print('    packaging =', packaging)

    baseUrl = makeArtifactEndpoint(host, repository)
    servicesEndpoint = makeServiceEndpoint(host, repository)

    if verbose:
        print('    baseUrl =', baseUrl)
        print('    version =', version)

    if version == 'SNAPSHOT':
        fileUrl = makeSnapshotFileUrl(baseUrl, groupId, artifactId)

    else:
        if version == 'NEXT':
            releaseNumber = getReleaseNumberFromMetadata(baseUrl, groupId, artifactId)
            version = generateNextVersion(releaseNumber)

        print('version = ' + version)
        fileUrl = makeReleaseFileUrl(baseUrl, groupId, artifactId, version)

    if verbose:
        print('    fileUrl =', fileUrl)

    # Upload base file
    file = open(localfile, 'rb')
    uploadFileAndHashes(file, fileUrl + '.' + packaging)
    file.close()

    # Upload the pom file
    file = makePom(groupId, artifactId, version, packaging)
    uploadFileAndHashes(file, fileUrl + '.' + 'pom')
    file.close()

    # Send request to Nexus to rebuild metadata
    url = makeMetadataUrl(servicesEndpoint, groupId, artifactId)
    rebuildMetadata(url)


####################################################################################################
# Main Routine
####################################################################################################

def main(argv):

    ####################################################################################################
    # Parse command line arguments
    ####################################################################################################

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('targets', type=str, nargs='*', help='a target to be built (default: all)')
    parser.add_argument("-r", "--release", help="Release a given version")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if len(args.targets) == 0:
        targets = ['clean', 'generate', 'configure', 'make', 'dist', 'deploy']
    else:
        targets = args.targets

    if args.release:
        global version
        version = args.release

    if args.verbose:
        global verbose
        verbose = args.verbose

        print('Given targets:  ', args.targets)
        print('Actual targets: ', targets)


    ####################################################################################################
    # Detect the environment
    ####################################################################################################
    if platform.system().startswith("Linux"):
        operatingSystem = 'Linux'

    elif platform.system().startswith("CYGWIN"):
        operatingSystem = 'Cygwin'

    elif platform.system().startswith("Windows"):

        if os.environ.get("MSYSTEM"):
            operatingSystem = 'MinGW'

        else:
            operatingSystem = 'Windows'

    else:
        print('The OperatingSystem is not defined')
        sys.exit(1)


    if operatingSystem == 'Windows':
        if os.path.exists(os.environ['ProgramFiles(x86)']):
            architecture = 'x86_64'
        else:
            architecture = 'x86'

        if which('cl.exe'):
            linker = 'msvc'
        else:
            print('The complier CL.EXE is not available')
            sys.exit(1)

        aol = architecture + '-' + operatingSystem + '-' + linker


    elif operatingSystem == 'undefined':
        aol = 'undefined'

    else:
        if which('gcc'):
            gcc = 'gcc'

        elif which('gcc.exe'):
            gcc = 'gcc.exe'

        else:
            print('The Compiler gcc is not available')
            sys.exit(1)

        stdout, stderr, returncode = runProgram ([gcc, '-v'], os.getcwd(), os.environ)

        lines = stderr.splitlines()
        for line in lines:
            if line.startswith('Target:'):
                words = line.split()
                aol = words[1]
                break

        string = aol.split('-')
        architecture = string[0]
        operatingSystem = string[1]
        linker = string[2]

    if verbose:
        print('architecture    =', architecture)
        print('operatingSystem =', operatingSystem)
        print('linker          =', linker)

    print('AOL =', aol)

    # Windows      x86_64-Windows-msvc
    # Linux        x86_64-linux-gnu
    # Cygwin       x86_64-pc-cygwin
    # MinGW        i686-w64-mingw32

    ####################################################################################################
    # Init
    ####################################################################################################

    src = os.path.abspath('./src')
    build = os.path.abspath('./build')
    source = os.path.abspath(build + '/source')
    sourcesrc = os.path.abspath(source + '/src')
    temp = os.path.abspath(build + '/temp')
    output = os.path.abspath(build + '/output')
    dist = os.path.abspath(build + '/dist')

    JANSSON_VERSION = '2.9'
    GROUPID = 'com.rsmaxwell.jannson.' + JANSSON_VERSION.replace('.', '-')
    ARTIFACTID = 'jannson-' + JANSSON_VERSION + '-' + aol
    PACKAGING = 'zip'
    REPOSITORYID = 'MaxwellHouse'
    HOST = 'www.rsmaxwell.co.uk'

    localfile = os.path.abspath(build + '/dist/' + ARTIFACTID)


    repository = 'releases'
    if version == 'SNAPSHOT':
        repository = 'snapshots'

    if verbose:
        print('version = ', version)
        print('repository = ', repository)

    ####################################################################################################
    # Clean
    ####################################################################################################

    if 'clean' in targets:
        print('target = clean')
        shutil.rmtree(build, ignore_errors=True)

    ####################################################################################################
    # Build the source directory
    ####################################################################################################

    if 'generate' in targets:

        print('target = generate')

        if not os.path.exists(temp):
            os.makedirs(temp)

        print('src = ' + src + '/' + 'jansson-2.9.tar.gz')

        # Download the jansson package
        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, temp + '/jansson-2.9.tar.gz')

        # Expand the archieve

        inF = gzip.GzipFile(temp + '/jansson-2.9.tar.gz', 'rb')
        s = inF.read()
        inF.close()

        outF = open(temp + '/jansson-2.9.tar', 'wb')
        outF.write(s)
        outF.close()

        tar = tarfile.open(temp + '/jansson-2.9.tar')
        tar.extractall(temp + '')
        tar.close()

        shutil.copytree(temp + '/jansson-2.9', source)


    ####################################################################################################
    # Configure
    ####################################################################################################

    if 'configure' in targets:

        print('target = configure')

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
            inplace_change(filename, '@json_inline@', '__inline')
            inplace_change(filename, '@json_have_long_long@', '1')
            inplace_change(filename, '@json_have_localeconv@', '1')

        else:     # Linux or MinGW or CygWin

            script = os.path.join(source, 'configure')
            os.chmod(script, 0o777)

            args = []
            args.append('bash')
            args.append(script)
            args.append('--prefix=' + location)

            runProgram(args, source, os.environ)


    ####################################################################################################
    # Make
    ####################################################################################################

    if 'make' in targets:

        print('target = make')

        if operatingSystem == 'Windows':

            print('operatingSystem = Windows')

            environ = os.environ
            environ['BUILD_TYPE'] = 'normal'
            environ['SOURCE'] = sourcesrc
            environ['OUTPUT'] = output
            runProgram (['make', '-f', src + '/make/' + aol + '.makefile', 'all'], output, environ)


        else:     # Linux or MinGW or CygWin
            runProgram (['make', 'clean'], source, os.environ)
            runProgram (['make'], source, os.environ)
            runProgram (['make', 'install'], source, os.environ)


    ####################################################################################################
    # Make the distribution
    ####################################################################################################

    if 'dist' in targets:

        print('target = dist')

        if operatingSystem == 'Windows':

            shutil.rmtree(build + '/dist', ignore_errors=True)

            location = os.path.join(dist + '/headers')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(sourcesrc + '/jansson.h', dist + '/headers/jansson.h')

            location = os.path.join(dist + '/libs/shared')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(output + '/shared/jansson.lib', dist + '/libs/shared/jansson.lib' )
            shutil.copy2(output + '/shared/jansson.dll', dist + '/libs/shared/jansson.dll' )

            location = os.path.join(dist + '/libs/static')
            if not os.path.exists(location):
                os.makedirs(location)

            shutil.copy2(output + '/static/jansson.lib', dist + '/libs/static/jansson.lib' )

#        else:     # Linux or MinGW or CygWin

        shutil.make_archive(localfile, PACKAGING, build + '/dist')

    ####################################################################################################
    # Deploy to nexus
    ####################################################################################################

    if 'deploy' in targets:
        uploadArtifact(HOST, repository, GROUPID, ARTIFACTID, PACKAGING, localfile + '.' + PACKAGING)


####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    main(sys.argv)
