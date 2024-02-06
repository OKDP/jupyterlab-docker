import json
import yaml
import argparse
import logging
from okdp.extension.matrix.constants import *

from okdp.extension.matrix.utils.matrix_utils import ignore_invalid_versions, join_versions, group_versions_by, normalize_matrix, normalize_scala_version, normalize_value, remove_duplicates
from okdp.extension.matrix.utils.matrix_utils import group_on

LOGGER = logging.getLogger(__name__)

class VersionCompatibilityMatrix:
   
   def __init__(self, path: str, git_branch: str):
      
      LOGGER.info(f"Building version compatibilty matrix - Matrix path: {path}, Current git branch: {git_branch}")

      with open(path, 'r') as file:
        doc = yaml.safe_load(file)
        self.compatibility_matrix = doc.get("compatibility-matrix")
        self.build_matrix = doc.get("build-matrix")
        self.build_matrix = self.build_matrix if self.build_matrix  else {}
        # Handle branches like: feature/my-feature
        self.git_branch = git_branch.replace("/", "-")

      self.__validate__()
      self._normalize_values_()

    
   def _normalize_values_(self):
      """"Convert simple value to an array
          Ex.: python_version: 3.11 => python_version: ['3.11']
      """
      self.compatibility_matrix = [dict(map(lambda kv: (kv[0], normalize_value(kv[1])), e.items())) for e in self.compatibility_matrix]
      self.build_matrix = dict(map(lambda kv: (kv[0], normalize_value(kv[1])), self.build_matrix.items()))

   def __validate__(self):
      if not self.compatibility_matrix:
        raise ValueError(f"The compatibility-matrix section is mandatory")

   def generate_matrix(self) -> (str, dict):

      compatibility_versions_matrix = [dict(map(lambda kv: (kv[0], normalize_value(kv[1])), e.items())) for e in self.compatibility_matrix]
      spark_version_matrix = normalize_matrix(ignore_invalid_versions(join_versions(group_versions_by(compatibility_versions_matrix, group_on=group_on), self.build_matrix)))
      spark_version_matrix = normalize_scala_version(self.add_latest_dev_tags(spark_version_matrix))
      python_version_matrix = remove_duplicates([{PYTHON_VERSION: e.get(PYTHON_VERSION), PYTHON_DEV_TAG: e.get(PYTHON_DEV_TAG)}  for e in spark_version_matrix ])
      return (spark_version_matrix, python_version_matrix)
   
   def add_latest_dev_tags(self, matrix: list[dict]) -> list[dict]:
      """ The intermediate images are pushed with a latest uniq dev tag """
      for e in matrix:
        e |= {f"{SPARK_DEV_TAG}": self.spark_dev_tag(e)}
        e |= {f"{PYTHON_DEV_TAG}": self.python_dev_tag(e.get(PYTHON_VERSION))}
      return matrix

   def python_dev_tag (self, python_version: str) -> str:
      return f"python{python_version}-{self.git_branch}-latest"

   def spark_dev_tag(self, e: dict) -> str:
      python_version = e.get(PYTHON_VERSION)
      spark_version = e.get(SPARK_VERSION)
      java_version = e.get(JAVA_VERSION)
      scala_version = e.get(SCALA_VERSION)
      scala_version = "2.12" if not scala_version else scala_version
      return f"spark{spark_version}-python{python_version}-java{java_version}-scala{scala_version}-{self.git_branch}-latest"

if __name__ == "__main__":
    
  logging.basicConfig(level=logging.INFO)
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument(
      "--versions-matrix-path",
      required=True,
      help="The matrix path location containing the versions to build",
  )

  arg_parser.add_argument(
      "--git-branch",
      required=True,
      help="The current git branch",
  )
  
  args = arg_parser.parse_args()
  vcm = VersionCompatibilityMatrix(args.versions_matrix_path, args.git_branch)
  #vcm = VersionCompatibilityMatrix(".build/.versions.yml", "main")
  #with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
  #  print(f"spark_matrix={json.dumps(vcm.generate_matrix())}", file=fh)
  (spark_matrix, python_version) = vcm.generate_matrix()
  assert spark_matrix, ("The resulting build matrix was empty. Please, review your configuration '.build/.versions.yml'") 
  print(f"spark={json.dumps(spark_matrix)}")
  print(f"python={json.dumps(python_version)}")
