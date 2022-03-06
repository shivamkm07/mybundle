import argparse
from errno import ESTALE
from fileinput import filename
import subprocess
import tarfile
import zipfile
import requests
import json
import os
import sys
import shutil



# GitHub Organization and repo name to download release
GITHUB_ORG="dapr"
GITHUB_DAPR_REPO="dapr"
GITHUB_DASHBOARD_REPO="dashboard"
GITHUB_CLI_REPO="cli"

# Dapr binaries filename
DAPRD_FILENAME="daprd"
PLACEMENT_FILENAME="placement"
DASHBOARD_FILENAME="dashboard"
CLI_FILENAME="dapr"
DAPRBUNDLE_FILENAME="daprbundle"

BIN_DIR="dist"
IMAGE_DIR="docker"
BUNDLE_DIR="daprbundle"
ARCHIVE_DIR="archive"

global runtime_os,runtime_arch,runtime_ver,dashboard_ver,cli_ver

def getLatestRelease(repo):
    daprReleaseUrl = "https://api.github.com/repos/" + GITHUB_ORG + "/" + repo + "/releases"
    print(daprReleaseUrl)
    latest_release = ""
    resp = requests.get(daprReleaseUrl).text
    data = json.loads(resp)
    print(data[0]['tag_name'])
    return data[0]['tag_name']

def binaryFileName(fileBase):
    if(runtime_os == "windows"):
        ext = "zip"
    else:
        ext = "tar.gz"
    fileName = f"{fileBase}_{runtime_os}_{runtime_arch}.{ext}"
    return fileName

def make_archive(src,dest,fileBase):
    print(f"Archiving {src} to {os.path.join(dest,binaryFileName(fileBase))}")
    fileNameBase = f"{fileBase}_{runtime_os}_{runtime_arch}"
    filePathBase = os.path.join(dest,fileNameBase)
    if runtime_os == "windows":
        shutil.make_archive(filePathBase,"zip",".",src)
    else:
        shutil.make_archive(filePathBase,"gztar",".",src)


def unpack_archive(filePath,dir):
    print(f"Extracting {filePath} to {dir}")
    if filePath.endswith('.zip'):
        shutil.unpack_archive(filePath,dir,"zip")
    else:
        if filePath.endswith('.tar.gz'):
            shutil.unpack_archive(filePath,dir,"gztar")
        else:
            print(f"Unknown archive file {filePath}")
            sys.exit(1)


def downloadBinary(repo, fileBase, version, out_dir):
    fileName = binaryFileName(fileBase)
    url = f"https://github.com/{GITHUB_ORG}/{repo}/releases/download/{version}/{fileName}"
    downloadPath = os.path.join(out_dir,fileName)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"Downloading {url} to {downloadPath}")

    resp = requests.get(url,stream=True)
    if resp.status_code == 200:
        with open(downloadPath, 'wb') as f:
            f.write(resp.raw.read())
    else:
        print(f"Error: Unable to Download {url}")

    print(f"Downloaded {url} to {downloadPath}")

def downloadBinaries(dir):
    bin_dir = os.path.join(dir,BIN_DIR)
    downloadBinary(GITHUB_DAPR_REPO,DAPRD_FILENAME,runtime_ver,bin_dir)
    downloadBinary(GITHUB_DAPR_REPO,PLACEMENT_FILENAME,runtime_ver,bin_dir)
    downloadBinary(GITHUB_DASHBOARD_REPO,DASHBOARD_FILENAME,dashboard_ver,bin_dir)
    downloadBinary(GITHUB_CLI_REPO,CLI_FILENAME,cli_ver,dir)

    cli_filepath = os.path.join(dir,binaryFileName(CLI_FILENAME))
    unpack_archive(cli_filepath,dir)
    os.remove(cli_filepath)


def downloadDockerImage(image_name, version, out_dir):
    docker_image=f"{image_name}:{version}"
    if (version == "latest"):
        docker_image =image_name
    fileName= docker_image.replace("/","-").replace(":","-") + ".tar.gz"
    downloadPath = os.path.join(out_dir,fileName)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"Downloading {docker_image} to {downloadPath}")

    cmd = ["docker", "pull",docker_image]
    completed_process = subprocess.run(cmd,text=True)
    if(completed_process.returncode != 0):
        print(f"Error pulling docker image {docker_image}")
        sys.exit(1)
    
    cmd = ["docker", "save", "-o", downloadPath, docker_image]
    completed_process = subprocess.run(cmd,text=True)
    if(completed_process.returncode != 0):
        print(f"Error saving docker image {docker_image}")
        sys.exit(1)

    print(f"Downloaded {docker_image} to {downloadPath}")

def downloadDockerImages(dir):
    if runtime_os == "darwin":
        return
    image_dir = os.path.join(dir,IMAGE_DIR)
    image_runtime_ver = runtime_ver.lstrip("v")
    downloadDockerImage("daprio/dapr",image_runtime_ver,image_dir)

def parseArguments():
    global runtime_os,runtime_arch,runtime_ver,dashboard_ver,cli_ver,ARCHIVE_DIR
    all_args = argparse.ArgumentParser()
    all_args.add_argument("--runtime_os",required=True,help="Runtime OS: [windows/linux/darwin]")
    all_args.add_argument("--runtime_arch",required=True,help="Runtime Architecture: [amd64/arm/arm64]")
    all_args.add_argument("--runtime_ver",default="latest",help="Dapr Runtime Version: default=latest")
    all_args.add_argument("--dashboard_ver",default="latest",help="Dapr Dashboard Version: default=latest")
    all_args.add_argument("--cli_ver",default="latest",help="Dapr CLI Version: default=latest")
    all_args.add_argument("--archive_dir",default="archive",help="Output Archive directory: default=archive")

    args = vars(all_args.parse_args())
    runtime_os = str(args['runtime_os'])
    runtime_arch = str(args['runtime_arch'])
    runtime_ver = str(args["runtime_ver"])
    dashboard_ver = str(args["dashboard_ver"])
    cli_ver = str(args["cli_ver"])
    ARCHIVE_DIR = str(args["archive_dir"])

    if runtime_ver == "latest":
        runtime_ver = getLatestRelease(GITHUB_DAPR_REPO)
    if dashboard_ver == "latest":
        dashboard_ver = getLatestRelease(GITHUB_DASHBOARD_REPO)
    if cli_ver == "latest":
        cli_ver = getLatestRelease(GITHUB_CLI_REPO)

def deleteIfExists(dir):
    if os.path.exists(dir):
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        else:
            os.remove(dir)

def write_version(dir):
    versions = {
        "daprd" : runtime_ver,
        "dashboard": dashboard_ver,
        "cli": cli_ver
    }
    jsonString = json.dumps(versions)
    filePath = os.path.join(dir,"version.json")
    with open(filePath,'w') as f:
        f.write(jsonString)


#############Main###################

#Parsing Arguments
parseArguments()

#Cleaning the bundle and archive  directory
deleteIfExists(BUNDLE_DIR)
deleteIfExists(ARCHIVE_DIR)

out_dir = BUNDLE_DIR
#Downloading Binaries
downloadBinaries(out_dir)

#Downloading Docker images
downloadDockerImages(out_dir)

#writing versions
write_version(out_dir)

#Archiving bundle
make_archive(BUNDLE_DIR,ARCHIVE_DIR,DAPRBUNDLE_FILENAME)
