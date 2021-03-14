import os
import subprocess
import pathlib
import json


def bash(cmd, cwd=".", stdout=None):
    subprocess.run(cmd.split(), cwd=cwd, stdout=stdout)


def diff_docker_saves(docker_folder):
    uncompressed = pathlib.Path(f"{docker_folder}/Dockerfile").read_text()
    bash("mkdir -p docker-compressor-input docker-compressor-output")
    bash(f"cp {docker_folder}/Dockerfile docker-compressor-input/Dockerfile")
    # Use compressor instead of just copying
    bash(f"cp docker-compressor-input/Dockerfile docker-compressor-output/Dockerfile.compressed")
    compressed_size = os.stat(f"docker-compressor-output/Dockerfile.compressed").st_size
    os.remove("docker-compressor-input/Dockerfile")
    os.rename("docker-compressor-output/Dockerfile.compressed", "docker-compressor-input/Dockerfile.compressed")
    # Use decompressor instead of just copying
    bash(f"cp docker-compressor-input/Dockerfile.compressed docker-compressor-output/Dockerfile.decompressed")
    decompressed = pathlib.Path("docker-compressor-output/Dockerfile.decompressed").read_text()
    if uncompressed == decompressed:
        bash("rm -rf docker-compressor-input docker-compressor-output")
        return compressed_size
    bash(f"cp -r {docker_folder} test1/")
    bash(f"cp -r {docker_folder} test2/")
    bash("mv docker-compressor-output/Dockerfile.decompressed test2/Dockerfile")
    bash("docker build --no-cache  -t uncompressed .", cwd="test1")
    os.mkdir("uncompressed")
    with open("uncompressed/uncompressed.tar", "w+") as uncompressed_tar:
        bash("docker save uncompressed", stdout=uncompressed_tar)

    bash("docker build --no-cache  -t decompressed .", cwd="test2")
    os.mkdir("decompressed")
    with open("decompressed/decompressed.tar", "w+") as decompressed_tar:
        bash("docker save decompressed", stdout=decompressed_tar)

    bash("tar -xf uncompressed.tar", cwd="uncompressed")
    bash("tar -xf decompressed.tar", cwd="decompressed")
    with open("uncompressed/manifest.json") as manifest:
        manifest_uncompressed = json.load(manifest)
    with open("decompressed/manifest.json") as manifest:
        manifest_decompressed = json.load(manifest)
    layers_uncompressed = manifest_uncompressed[0]["Layers"]
    layers_decompressed = manifest_decompressed[0]["Layers"]
    if len(layers_decompressed) == len(layers_decompressed):
        layer_comparisons = zip(layers_uncompressed, layers_decompressed)
        for layer_uncompressed, layer_decompressed in layer_comparisons:
            uncompressed_extracted_layer = layer_uncompressed[:-4]
            decompressed_extracted_layer = layer_decompressed[:-4]
            bash(f"mkdir uncompressed/{uncompressed_extracted_layer} decompressed/{decompressed_extracted_layer}")
            bash(f"tar -xf {layer_uncompressed} -C {uncompressed_extracted_layer}", cwd="uncompressed")
            bash(f"tar -xf {layer_decompressed} -C {decompressed_extracted_layer}", cwd="decompressed")

            diff_process = subprocess.Popen(f"diff -r uncompressed/{uncompressed_extracted_layer} decompressed/{decompressed_extracted_layer}".split(),
                                            stdout=subprocess.PIPE)
            diff_stdout = diff_process.communicate()[0]
            if len(diff_stdout) > 0:
                return len(uncompressed) * 10
    bash("rm -rf test1 test2 docker-compressor-input docker-compressor-output uncompressed decompressed")
    return compressed_size


diff_docker_saves("docker_project")
