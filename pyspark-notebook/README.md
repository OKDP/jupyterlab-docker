# Dockerfiles patchs

The directory contains a list of patchs for original dockerfiles:

## List of patchs:

[PySpark 3.2.x java 11 support](patch/pyspark-notebook/Dockerfile.spark3.2.x#L6):  Add  "--add-opens options" to be compatible with java 11 (<=3.2.x)

The options are picked from the java module: [JavaModuleOptions.java](https://github.com/apache/spark/blob/8706ccdf461c3b7f82b94b9e953ca4547f551ab1/launcher/src/main/java/org/apache/spark/launcher/JavaModuleOptions.java)

Please, checkk the following guide: [migrating-jdk-8-later-jdk-releases](https://docs.oracle.com/en/java/javase/16/migrate/migrating-jdk-8-later-jdk-releases.html#GUID-2F61F3A9-0979-46A4-8B49-325BA0EE8B66) for more information


