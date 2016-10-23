

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
import json



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

def runProgram(debug, workingDirectory, environment, arguments):

    if debug:
        print('------------------------------------------------------------------------------------')
        print('subprocess:', arguments)
        #print('workingDirectory = ' + workingDirectory)
        #print('environment:', environment)

    p = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, cwd=workingDirectory)
    stdout = p.stdout.read().decode('utf-8')
    stderr = p.stderr.read().decode('utf-8')
    returncode = p.returncode

    if debug:
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

    if args.debug:
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

    if args.debug:
        print('    release =', release.text)

    return release.text


####################################################################################################
# Parse the build number from the metadata
####################################################################################################

def parseBuildNumberFromMetadata(debug, content):

    if debug:
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

    if debug:
        print('    buildNumber =', buildNumber.text)

    return int(buildNumber.text)


####################################################################################################
# Read the metadata and return the version
####################################################################################################

def getBuildNumberFromMetadata(debug, baseUrl, repositoryPath, groupId, artifactId, version):

    if debug:
        print('getBuildNumberFromMetadata:')
        print('    baseUrl = ' + baseUrl)
        print('    repositoryPath = ' + repositoryPath)
        print('    artifactId = ' + artifactId)
        print('    version = ' + version)

    metadataUrl = baseUrl + repositoryPath + '/' + groupId.replace('.', '/') + '/' + artifactId + '/' + version + '/' + 'maven-metadata.xml'

    if debug:
        print('    metadataUrl = ' + metadataUrl)

    # Get the metadata to discover the current build number
    r = requests.get(metadataUrl, stream=True)

    # Use the metadata file to work out the build number
    if r.status_code == 200: # http.HTTPStatus.OK.value
        if debug:
            print('getBuildNumberFromMetadata')
            print('    Artifact was found in Nexus')

        buildNumber = 1 + parseBuildNumberFromMetadata(debug, r.text)

    elif r.status_code == 404: # http.HTTPStatus.NOT_FOUND.value
        if debug:
            print('getBuildNumberFromMetadata')
            print('    Artifact not found in Nexus')
        buildNumber = 1

    else:
        print('Unexpected Http response ' + str(r.status_code) + ' when getting: maven-metadata.xml')
        print('    metadataUrl: ' + metadataUrl)
        content = r.raw.decode('utf-8')
        print('Content =', content)
        sys.exit(99)

    if debug:
        print('buildNumber = ' + str(buildNumber))

    return str(buildNumber)


####################################################################################################
# Delete a URL resource
#
# Make the Nexus repository rebuild its metadata
# curl -v --request DELETE  --user "login:password"  --silent http://nexusHost/service/local/metadata/repositories/myRepository/content
#
####################################################################################################

def rebuildMetadata(debug, base, pathname):

    if debug:
        print('rebuildMetadata')
        print('    base =', base)
        print('    pathname =', pathname)

    url = base + pathname

    if debug:
        print('    url = ' + url)

    USER=os.environ["MAXWELLHOUSE_ADMIN_USER"]
    PASSWORD=os.environ["MAXWELLHOUSE_ADMIN_PASS"]

    r = requests.delete(url, auth=(USER, PASSWORD))
    statusCode = r.status_code

    if debug:
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

    if args.debug:
        print('download')
        print('    url =', url)
        print('    statusCode =', statusCode)

    return r


####################################################################################################
# Upload a stream to a URL
####################################################################################################

def uploadFile(debug, file, url):

    if debug:
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

    if debug:
        print('    statusCode =', statusCode)

    return statusCode


####################################################################################################
# Upload a string
####################################################################################################

def uploadString(debug, string, url):

    if debug:
        print("uploadString")
        print("    string =", string)

    file = io.StringIO(string)
    uploadFile(debug, file, url)
    file.close()


####################################################################################################
# Upload a file and its metadata to Artifact
####################################################################################################

def uploadFileAndHashes(debug, file, base, filePath, fileName, packaging):

    if debug:
        print('uploadFileAndHashes:')
        print('    base = ', base)
        print('    filePath = ', filePath)
        print('    fileName = ', fileName)
        print('    packaging = ', packaging)

    url = base + filePath + '/' + fileName + '.' + packaging

    if debug:
        print('    url = ', url)

    uploadFile(debug, file, url)
    uploadString(debug, md5(file), url + '.md5')
    uploadString(debug, sha1(file), url + '.sha1')


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

def uploadArtifact(debug, base, groupId, artifactId, version, packaging, localfile):

    if debug:
        print('uploadArtifact')
        print('    base =', base)
        print('    groupId =', groupId)
        print('    artifactId =', artifactId)
        print('    version =', version)
        print('    packaging =', packaging)

    snap = version.endswith('SNAPSHOT')

    if snap:
        repository = 'snapshots'
        timestamp = '{:%Y%m%d.%H%M%S}'.format(datetime.datetime.now())
        repositoryPath = '/service/local/repositories/' + repository + '/content/'
        buildNumber = getBuildNumberFromMetadata(debug, base, repositoryPath, groupId, artifactId, version)
        fileName = artifactId + '-' + version.replace('SNAPSHOT', timestamp) + '-' + buildNumber
    else:
        repository = 'releases'
        repositoryPath = '/service/local/repositories/' + repository + '/content/'
        fileName = artifactId

    filePath = repositoryPath + groupId.replace('.', '/') + '/' + artifactId + '/' + version

    # Upload base file
    file = open(localfile, 'rb')
    uploadFileAndHashes(debug, file, base, filePath, fileName, packaging)
    file.close()

    # Upload the pom file
    file = makePom(groupId, artifactId, version, packaging)
    uploadFileAndHashes(debug, file, base, filePath, fileName, 'pom')
    file.close()

    # Send request to Nexus to rebuild metadata
    servicesPath = '/service/local/metadata/repositories/' + repository + '/content/' + groupId.replace('.', '/') + '/' + artifactId
    rebuildMetadata(debug, base, servicesPath)


####################################################################################################
# Main Routine
####################################################################################################

def main(argv):

    ####################################################################################################
    # Parse command line arguments
    ####################################################################################################

    parser = argparse.ArgumentParser(description='Build and deploy a project.')

    parser.add_argument('goals', type=str, nargs='*', help='A list of build goals [default: all]')
    parser.add_argument("-f", "--file", help="Build file [default: build.json]", default='build.json')
    parser.add_argument("-X", "--debug", help="Increase output verbosity", action="store_true", default=False)
    parser.add_argument("-v", "--version", help="Set the release verson [default = 'version' field in build.json]")

    args = parser.parse_args()

    if len(args.goals) == 0:
        goals = ['clean', 'generate', 'configure', 'make', 'dist', 'deploy']
    else:
        goals = args.goals

    if args.debug:
        print('Given goals:  ', args.goals)
        print('Actual goals: ', goals)


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

        stdout, stderr, returncode = runProgram(args.debug, os.getcwd(), os.environ, [gcc, '-v'])

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

    if args.debug:
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

    with open(args.file) as buildfile:
        bob = json.load(buildfile)

    src = os.path.abspath('./src')
    build = os.path.abspath('./build')
    source = os.path.abspath(build + '/source')
    sourcesrc = os.path.abspath(source + '/src')
    temp = os.path.abspath(build + '/temp')
    output = os.path.abspath(build + '/output')
    dist = os.path.abspath(build + '/dist')

    GROUPID = bob["groupId"]
    ARTIFACTID = bob["artifactId"] + '-' + aol
    PACKAGING = 'zip'
    REPOSITORYID = 'MaxwellHouse'
    HOST = 'www.rsmaxwell.co.uk'
    BASE = bob["distributionManagement"]["repository"]["url"]

    if args.version == None:
        VERSION = bob["version"]
    else:
        VERSION = args.version

    if args.debug:
        print('VERSION = ' + VERSION)

    localfile = os.path.abspath(build + '/dist/' + ARTIFACTID)

    ####################################################################################################
    # Clean
    ####################################################################################################

    if 'clean' in goals:
        print('goal = clean')
        shutil.rmtree(build, ignore_errors=True)

    ####################################################################################################
    # Build the source directory
    ####################################################################################################

    if 'generate' in goals:

        print('goal = generate')

        if not os.path.exists(temp):
            os.makedirs(temp)

        targz = os.path.abspath(temp + '/' + 'jansson-2.9.tar.gz')

        if args.debug:
            print('src = ' + targz)

        # Download the jansson package
        url = 'http://www.digip.org/jansson/releases/jansson-2.9.tar.gz'
        urllib.request.urlretrieve(url, targz)

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

    if 'configure' in goals:

        print('goal = configure')

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

            runProgram(args.debug, source, os.environ, args)


    ####################################################################################################
    # Make
    ####################################################################################################

    if 'make' in goals:

        print('goal = make')

        if operatingSystem == 'Windows':
            environ = os.environ
            environ['BUILD_TYPE'] = 'normal'
            environ['SOURCE'] = sourcesrc
            environ['OUTPUT'] = output
            runProgram(args.debug, output, environ, ['make', '-f', src + '/make/' + aol + '.makefile', 'all'])


        else:     # Linux or MinGW or CygWin
            runProgram(args.debug, source, os.environ, ['make', 'clean'])
            runProgram(args.debug, source, os.environ, ['make'])
            runProgram(args.debug, source, os.environ, ['make', 'install'])


    ####################################################################################################
    # Make the distribution
    ####################################################################################################

    if 'dist' in goals:

        print('goal = dist')

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

    if 'deploy' in goals:
        uploadArtifact(args.debug, BASE, GROUPID, ARTIFACTID, VERSION, PACKAGING, localfile + '.' + PACKAGING)


    ####################################################################################################
    # Report success
    ####################################################################################################
    print('')
    print('SUCCESS')

####################################################################################################
# Call main routine
####################################################################################################

if __name__ == "__main__":
    main(sys.argv)
