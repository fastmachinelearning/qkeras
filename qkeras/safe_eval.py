# Copyright 2019 Google LLC
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Implements a safe evaluation using globals()."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pyparsing import delimitedList
from pyparsing import Group
from pyparsing import Optional
from pyparsing import Regex
from pyparsing import Suppress


def Num(s):
  """Tries to convert string to either int or float."""
  try:
    try:
      return int(s)
    except ValueError:
      return float(s)
  except ValueError:
    return s


def GetParams(s):
  """Extracts args and kwargs from string."""
  # modified from https://stackoverflow.com/questions/38799223/parse-string-to-identify-kwargs-and-args  # pylint: disable=line-too-long

  _lparen = Suppress("(")  # pylint: disable=invalid-name
  _rparen = Suppress(")")  # pylint: disable=invalid-name
  _eq = Suppress("=")  # pylint: disable=invalid-name

  data = (_lparen + Optional(
      delimitedList(
          Group(Regex(r"[^=,)\s]+") + Optional(_eq + Regex(u"[^,)]*")))
          )
      ) + _rparen)

  items = data.parseString(s).asList()

  # need to make sure that kwargs only happen after args are processed
  args = [Num(i[0]) for i in items if len(i) == 1]
  kwargs = {i[0]: Num(i[1]) for i in items if len(i) == 2}

  # check for syntax error
  for i in range(1, len(items)):
    if (len(items[i]) == 1) and (len(items[i-1]) == 2):
      raise SyntaxError

  return args, kwargs


def safe_eval(eval_str, op_dict, *params, **kwparams):  # pylint: disable=invalid-name
  """Replaces eval by a safe eval mechanism."""

  function_split = eval_str.split("(")
  quantizer = op_dict[function_split[0]]

  if len(function_split) == 2:
    args, kwargs = GetParams("(" + function_split[1])
  else:
    args = []
    kwargs = {}

  args = args + list(params)
  for k in kwparams:
    kwargs[k] = kwparams[k]

  if len(function_split) == 2 or args or kwargs:
    return quantizer(*args, **kwargs)
  else:
    if isinstance(quantizer, type):
      return quantizer()
    else:
      return quantizer
