from tests.extension.matrix.conftest import MockedVersionCompatibilityMatrix, to_dict
from okdp.extension.matrix.utils.matrix_utils import group_versions_by
from okdp.extension.matrix.utils.matrix_utils import group_on
from okdp.extension.matrix.version_compatibility_matrix import VersionCompatibilityMatrix

def test_group_versions_by(
    version_compatibility_matrix_data: list[dict],
) -> None:
    # Given: version_compatibility_matrix_data
    # Expected:
    expected = """[
    {
        "python_version": ["3.10"],
        "spark_version": ["3.3.1","3.3.2","3.3.3","3.3.4"],
        "java_version": ["17"],
        "scala_version": ["2.12","2.13"],
        "hadoop_version": ["3"],
        "spark_download_url": ["https://archive.apache.org/dist/spark/"]
    },{
        "python_version": ["3.11"],
        "spark_version": ["3.5.0"],
        "java_version": ["17","21"],
        "scala_version": ["2.12","2.13"],
        "hadoop_version": ["3"],
        "spark_download_url": ["https://archive.apache.org/dist/spark/"]
    },{
        "python_version": ["3.11"],
        "spark_version": ["3.4.1","3.4.2"],
        "java_version": ["17"],
        "scala_version": ["2.12","2.13"],
        "hadoop_version": ["3"],
        "spark_download_url": ["https://archive.apache.org/dist/spark/"]
    },{
        "python_version": ["3.9"],
        "spark_version": [ "3.2.1", "3.2.2", "3.2.3", "3.2.4"],
        "java_version": ["11"],
        "scala_version": ["2.12", "2.13"],
        "hadoop_version": ["3.2"],
        "spark_download_url": ["https://archive.apache.org/dist/spark/"]
    }
    ]
    """
    assert group_versions_by(version_compatibility_matrix_data, group_on=group_on) == to_dict(expected)

def test_build_matrix_empty(
    version_compatibility_matrix_data: list[dict],
) -> None:
    # Given: version_compatibility_matrix_data
    version_compatibility_matrix = version_compatibility_matrix_data
    build_matrix = {}
   
    # When:
    vcm = MockedVersionCompatibilityMatrix(compatibility_matrix = version_compatibility_matrix, 
                                           build_matrix = build_matrix, 
                                           git_branch="main")
    vcm._normalize_values_()
    (spark_matrix, python_version) = vcm.generate_matrix()

    # Then: check the number of combinations when the build_matrix is empty
    expected_nb_combinations = 24
    actual_nb_combinations = len(spark_matrix)
    assert actual_nb_combinations == expected_nb_combinations, f"The number of elements should be {expected_nb_combinations}, got {actual_nb_combinations}"

    # Then: check the expected combinations when the build_matrix is empty
    with open("python/tests/extension/matrix/resources/expected_build_matrix_empty.json", 'r') as file:
         expected_build_matrix_empty = file.read()  

    assert to_dict(expected_build_matrix_empty) == spark_matrix

def test_filter_spark_version(
    version_compatibility_matrix_data: list[dict],
) -> None:
    # Given: version_compatibility_matrix_data
    version_compatibility_matrix = version_compatibility_matrix_data
    build_matrix = {"spark_version": "3.2.4"}
   
    # When:
    vcm = MockedVersionCompatibilityMatrix(compatibility_matrix = version_compatibility_matrix, 
                                           build_matrix = build_matrix, 
                                           git_branch="main")
    vcm._normalize_values_()
    (spark_matrix, python_version) = vcm.generate_matrix()

    # Then: check the number of combinations when the build_matrix is empty
    expected_nb_combinations = 2
    actual_nb_combinations = len(spark_matrix)
    expected_test_filter_spark_version = """[
      {
            "python_version": "3.9",
            "spark_version": "3.2.4",
            "java_version": "11",
            "scala_version": "",
            "hadoop_version": "3.2",
            "spark_download_url": "https://archive.apache.org/dist/spark/",
            "spark_dev_tag": "spark3.2.4-python3.9-java11-scala2.12-main-latest",
            "python_dev_tag": "python3.9-main-latest"
      },
      {
            "python_version": "3.9",
            "spark_version": "3.2.4",
            "java_version": "11",
            "scala_version": "2.13",
            "hadoop_version": "3.2",
            "spark_download_url": "https://archive.apache.org/dist/spark/",
            "spark_dev_tag": "spark3.2.4-python3.9-java11-scala2.13-main-latest",
            "python_dev_tag": "python3.9-main-latest"
      }
    ]"""
    assert actual_nb_combinations == expected_nb_combinations, f"The number of elements should be {expected_nb_combinations}, got {actual_nb_combinations}"
   
    assert spark_matrix == to_dict(expected_test_filter_spark_version)
    assert python_version == to_dict("""[{"python_version": "3.9", "python_dev_tag": "python3.9-main-latest"}]""")

def test_filter_spark_version_scala_version(
    version_compatibility_matrix_data: list[dict],
) -> None:
    # Given: version_compatibility_matrix_data
    version_compatibility_matrix = version_compatibility_matrix_data
    build_matrix = {"spark_version": "3.2.4", "scala_version": "2.13"}
   
    # When:
    vcm = MockedVersionCompatibilityMatrix(compatibility_matrix = version_compatibility_matrix, 
                                           build_matrix = build_matrix, 
                                           git_branch="main")
    vcm._normalize_values_()
    (spark_matrix, python_version) = vcm.generate_matrix()

    # Then: check the number of combinations when the build_matrix is empty
    expected_nb_combinations = 1
    actual_nb_combinations = len(spark_matrix)
    expected_test_filter_spark_version = """[
      {
            "python_version": "3.9",
            "spark_version": "3.2.4",
            "java_version": "11",
            "scala_version": "2.13",
            "hadoop_version": "3.2",
            "spark_download_url": "https://archive.apache.org/dist/spark/",
            "spark_dev_tag": "spark3.2.4-python3.9-java11-scala2.13-main-latest",
            "python_dev_tag": "python3.9-main-latest"
      }
    ]"""
    assert actual_nb_combinations == expected_nb_combinations, f"The number of elements should be {expected_nb_combinations}, got {actual_nb_combinations}"
   
    assert spark_matrix == to_dict(expected_test_filter_spark_version)
    assert python_version == to_dict("""[{"python_version": "3.9", "python_dev_tag": "python3.9-main-latest"}]""")
    
def test_filter_wrong_version(
    version_compatibility_matrix_data: list[dict],
) -> None:
    # Given: version_compatibility_matrix_data
    version_compatibility_matrix = version_compatibility_matrix_data
    # The python_version is not supported by the compatibilty matrix
    build_matrix = {"python_version": "3.7"}
   
    # When:
    vcm = MockedVersionCompatibilityMatrix(compatibility_matrix = version_compatibility_matrix, 
                                           build_matrix = build_matrix, 
                                           git_branch="main")
    vcm._normalize_values_()
    (spark_matrix, python_version) = vcm.generate_matrix()

    # Then: check the number of combinations when the build_matrix is empty
    expected_nb_combinations = 0
    actual_nb_combinations = len(spark_matrix)
    assert actual_nb_combinations == expected_nb_combinations, f"spark_matrix: The number of elements should be {expected_nb_combinations}, got {actual_nb_combinations}"
    assert len(python_version) == expected_nb_combinations, f"python_version: The number of elements should be {expected_nb_combinations}, got {actual_nb_combinations}"
   
