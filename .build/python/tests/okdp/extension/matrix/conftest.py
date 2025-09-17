import json
import pytest
from okdp.extension.matrix.version_compatibility_matrix import VersionCompatibilityMatrix  # type: ignore

class MockedVersionCompatibilityMatrix(VersionCompatibilityMatrix):
    def __init__(self, compatibility_matrix: str, build_matrix: str, git_branch: str):
        self.compatibility_matrix = compatibility_matrix
        self.build_matrix = build_matrix
        self.git_branch = git_branch
        
def to_dict(str_as_json: str) -> list[dict]:
   return json.loads(str_as_json)

@pytest.fixture(scope="module")
def version_compatibility_matrix_data():
    return [ 
            {'python_version': ['3.9'],
            'spark_version': ['3.2.1', '3.2.2', '3.2.3', '3.2.4'], 
            'java_version': ['11'], 
            'scala_version': ['2.12', '2.13'],
            'hadoop_version': ['3.2'],
            'spark_download_url': ['https://archive.apache.org/dist/spark/']
            },
            {'python_version': ['3.10'],
            'spark_version': ['3.3.1', '3.3.2', '3.3.3', '3.3.4'], 
            'java_version': ['17'], 
            'scala_version': ['2.12', '2.13'],
            'hadoop_version': ['3'],
            'spark_download_url': ['https://archive.apache.org/dist/spark/']
            },
            {'python_version': ['3.11'],
            'spark_version': ['3.4.1', '3.4.2'], 
            'java_version': ['17'], 
            'scala_version': ['2.12', '2.13'],
            'hadoop_version': ['3'],
            'spark_download_url': ['https://archive.apache.org/dist/spark/']
            },
            {'python_version': ['3.11'],
            'spark_version': ['3.5.0'], 
            'java_version': ['17', '21'], 
            'scala_version': ['2.12', '2.13'],
            'hadoop_version': ['3'],
            'spark_download_url': ['https://archive.apache.org/dist/spark/']
            }
  ]




