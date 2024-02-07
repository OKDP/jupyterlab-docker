
#### Add  "--add-opens options" to be compatible with java 11/17 (<=3.3.2)
#### The options are picked from the java module:
###### https://github.com/apache/spark/blob/8706ccdf461c3b7f82b94b9e953ca4547f551ab1/launcher/src/main/java/org/apache/spark/launcher/JavaModuleOptions.java
###### Doc: # https://docs.oracle.com/en/java/javase/16/migrate/migrating-jdk-8-later-jdk-releases.html#GUID-2F61F3A9-0979-46A4-8B49-325BA0EE8B66
ENV JDK_JAVA_OPTIONS $JDK_JAVA_OPTIONS \
    --add-opens=java.base/java.lang=ALL-UNNAMED \
    --add-opens=java.base/java.lang.invoke=ALL-UNNAMED \
    --add-opens=java.base/java.lang.reflect=ALL-UNNAMED \
    --add-opens=java.base/java.io=ALL-UNNAMED \
    --add-opens=java.base/java.net=ALL-UNNAMED \
    --add-opens=java.base/java.nio=ALL-UNNAMED \
    --add-opens=java.base/java.util=ALL-UNNAMED \
    --add-opens=java.base/java.util.concurrent=ALL-UNNAMED \
    --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED \
    --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED \
    --add-opens=java.base/sun.nio.ch=ALL-UNNAMED \
    --add-opens=java.base/sun.nio.cs=ALL-UNNAMED \
    --add-opens=java.base/sun.security.action=ALL-UNNAMED \
    --add-opens=java.base/sun.util.calendar=ALL-UNNAMED \
    --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED
