#
# Copyright 2026 The OKDP Authors.
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
#

from itertools import groupby
import itertools
from okdp.extension.matrix.constants import *

def group_on(elem) -> str:
    return str(elem[PYTHON_VERSION]) + "_".join(str(elem[JAVA_VERSION])) + str(elem[HADOOP_VERSION])

def intersect_dicts(dict1: dict, dict2: dict) -> dict:
    """ Intersection between values of two dicts 
        if dict2 is empty, return dict1
    """
    dict_res = {**dict1, **dict2}
    ### technical key for tag to build spark images without rebuilding bases images
    #for key in dict1.keys():
    #    if key == PYTHON_VERSION:
    #      dict_res[f"_{PYTHON_VERSION}"] = dict1.get(key)
    ### Do the intersection
    for key, value in dict_res.items():
        if key in dict1 and key in dict2:
                dict_res[key] = list(set(value) & set(dict1[key]))
    return dict_res

def merge_dicts(dict1: dict, *args: dict) -> dict:
    """ Merge multiple dicts by keeping all the values for the keys """
    if not args:
        return dict1
    dict2 = args[0]
    dict_res = {**dict1, **dict2}
    for key, value in dict_res.items():
        if key in dict1 and key in dict2:
                dict_res[key] = list(set(sum([value , dict1[key]], [])))
    return dict_res if len(args) == 1 else merge_dicts(dict_res, *args[1:])

def join_versions(groups: list[dict], on_dict: dict) -> list[dict]:
    """ Intersect groups of dicts values with the provided on_dict """
    ### Intersect the groups with on_dict
    result = []
    for group in groups:
      result.append(intersect_dicts(group, on_dict))
    
    return result

def group_versions_by(dicts: list[dict], group_on) -> list[dict]:
    """ Group the spark versions by PYTHON_VERSION/JAVA_VERSION/HADOOP_VERSION
    """
    ### Group the elements by python_version
    python_groups = []
    data = sorted(dicts, key=group_on)
    for k, g in groupby(data, group_on):
         python_groups.append(list(g))
    
    ### Merge the groups
    result = []
    for group in python_groups:
      result.extend(group)
    return result

def ignore_invalid_versions (dicts: list[dict]) -> list[dict]:
   return list(filter(lambda elem: 
                elem.get(SPARK_VERSION) and 
                elem.get(JAVA_VERSION) and 
                elem.get(SCALA_VERSION) and 
                elem.get(HADOOP_VERSION) and elem.get(SPARK_DOWNLOAD_URL),
                dicts))

def normalize_matrix(versions: list[dict]) -> list[dict]:
  """" Convert to an array matrix
       https://github.com/orgs/community/discussions/24981 
  """

  combinations = []
  for version in versions:
    keys, values = zip(*version.items())
    combinations.extend([dict(zip(keys, v)) for v in itertools.product(*values)])

  return combinations

def normalize_scala_version(matrix: list[dict]) -> list[dict]:
    """
    dist is prefixed with -scala2.13 for scala version 2.13 and spark version < 4
    Ex.: https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3-scala2.13.tgz 
    Normalize Scala version in the matrix:
    - If Scala version is 2.13, keep it; otherwise, set to empty string.
    - If Spark major version >= 4, set scala_version to empty string.
    """
    def normalize(key, value, row):
        if key == SCALA_VERSION:
            # Check Spark version as well
            spark_ver = row.get(SPARK_VERSION, "")
            major = int(spark_ver.split(".")[0]) if spark_ver else 0
            if major >= 4:
                return key, ""
            return key, value if value == "2.13" else ""
        return key, value

    return [dict(normalize(k, v, e) for k, v in e.items()) for e in matrix]

def normalize_value (value: str) -> [str]:
  """ Cast values to string and convert simple values to list for github strategy matrix input """
  if not type(value) == list:
    return [str(value)]
  return [str(v) for v in value]

def remove_duplicates (dicts: list[dict]) -> list[dict]:
    result = []
    for dict in dicts:
        if dict not in result:
            result.append(dict)
    return result

