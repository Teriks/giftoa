#!/usr/bin/python3

# Copyright (c) 2016, Teriks
# All rights reserved.

# package.py is part of giftoa

# giftoa is distributed under the following BSD 3-Clause License

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import sys
import re
import subprocess
import shutil


script_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.dirname(script_path)


rightgif_path = os.path.join(src_path, 'giftoa', 'rightgif.py')

giftoa_path = os.path.join(src_path, 'giftoa', 'giftoa.py')


simple_version_parse = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?$")


rightgif_version = simple_version_parse.match(
                   subprocess.check_output([sys.executable, rightgif_path, '-v']).decode('utf-8').split()[1]
                   )

giftoa_version = simple_version_parse.match(
                 subprocess.check_output([sys.executable, giftoa_path, '-v']).decode('utf-8').split()[1]
                 )


giftoa_debian_version = ".".join(giftoa_version.group(1,2,3))
if len(giftoa_version.groups()) > 3 and giftoa_version.group(4) != '0': 
    giftoa_debian_version += "-"+giftoa_version.group(4)


rightgif_debian_version = ".".join(rightgif_version.group(1,2,3))
if len(rightgif_version.groups()) > 3 and rightgif_version.group(4) != '0': 
    rightgif_debian_version += "-"+rightgif_version.group(4)


shutil.rmtree(os.path.join(script_path,'tmp'), ignore_errors=True)
shutil.rmtree(os.path.join(script_path,'bin'), ignore_errors=True)


giftoa_work_dir = os.path.join(script_path, 'tmp', 'giftoa')
rightgif_work_dir = os.path.join(script_path, 'tmp', 'rightgif')


os.makedirs(os.path.join(giftoa_work_dir,'DEBIAN'))
os.makedirs(os.path.join(giftoa_work_dir,'usr','bin'))


os.makedirs(os.path.join(rightgif_work_dir,'DEBIAN'))
os.makedirs(os.path.join(rightgif_work_dir,'usr','bin'))

giftoa_bin_path = os.path.join(giftoa_work_dir,'usr','bin','giftoa')
rightgif_bin_path = os.path.join(giftoa_work_dir,'usr','bin','rightgif')

shutil.copy(giftoa_path, giftoa_bin_path)
os.chmod(giftoa_bin_path, mode=0o755)

shutil.copy(rightgif_path, rightgif_bin_path)
os.chmod(rightgif_bin_path, mode=0o755)


with open(os.path.join(script_path,'templates','giftoa_control'), 'r') as template:
    with open(os.path.join(giftoa_work_dir,'DEBIAN','control'), 'w') as control:
        control.write(template.read().replace('{VERSION}', giftoa_debian_version))


with open(os.path.join(script_path,'templates','rightgif_control'), 'r') as template:
    with open(os.path.join(rightgif_work_dir,'DEBIAN','control'), 'w') as control:
        control.write(template.read().replace('{VERSION}', rightgif_debian_version))



os.makedirs(os.path.join(script_path,'bin'))


os.system('dpkg-deb --build {work_dir} {binpath}'
          .format(work_dir=giftoa_work_dir, 
                  binpath=os.path.join(script_path,'bin','giftoa_'+giftoa_debian_version+'.deb')))

os.system('dpkg-deb --build {work_dir} {binpath}'
          .format(work_dir=rightgif_work_dir, 
                  binpath=os.path.join(script_path,'bin','rightgif_'+rightgif_debian_version+'.deb')))


shutil.rmtree(os.path.join(script_path,'tmp'))









