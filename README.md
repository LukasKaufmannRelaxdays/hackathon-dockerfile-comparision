# hackathon-dockerfile-comparision
This file shows how we compare the uncompressed and the decompressed Dockerfiles according to their docker images.

This project was created in the Relaxdays Code Challenge Vol. 1. See https://sites.google.com/relaxdays.de/hackathon-relaxdays/startseite for more information. My participant ID in the challenge was: CC-VOL1-1

## How to run this project
You can get a running version of this code by using:
```bash
git clone https://github.com/LukasKaufmannRelaxdays/hackathon-dockerfile-comparision.git
```
Place any project with a Dockerfile which you want to test in the `docker_project` folder.

Put your docker command under the 
`# Use compressor instead of just copying`
and the
`# Use decompressor instead of just copying`
comments in the compare.py
