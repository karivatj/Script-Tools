###############################################################################
#
# Copyright (c) Crossbar.io Technologies GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################

from __future__ import print_function
from __future__ import unicode_literals

def format_measurement_data_to_plotly(data, key):
    t = sorted(data[key], key=lambda T: datetime.datetime.strptime(T[0], '%Y-%m-%d'))
    return [ { 'data': [ { 'x': [ T[0] for T in t ], 'y': [ T[1] for T in t ] } ] } ]

def format_bloodpressure_data_to_plotly(data, key):
    t = sorted(data[key], key=lambda T: datetime.datetime.strptime(T[0], '%Y-%m-%d'))    
    return [ { 'data': [ { 'x': [ T[0] for T in t ], 'y': [ T[1][0] for T in t ] }, { 'x': [ T[0] for T in t ], 'y': [ T[1][1] for T in t ] }] } ]
