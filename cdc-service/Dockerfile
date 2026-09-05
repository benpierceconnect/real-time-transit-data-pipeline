FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN mvn -B -ntp dependency:go-offline
COPY src ./src
RUN mvn -B -ntp test package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /build/target/transit-cdc-service.jar /app/transit-cdc-service.jar
RUN mkdir -p /state && chown -R 10001:10001 /app /state
USER 10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/transit-cdc-service.jar"]
