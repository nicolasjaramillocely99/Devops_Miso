# Analisis de monitoreo continuo con New Relic

## Objetivo

Monitorear la API de blacklist desplegada en AWS Fargate para detectar fallos,
latencia alta, errores HTTP y problemas de infraestructura durante la operacion.

## Alcance

La configuracion se divide en dos niveles:

1. **APM de la aplicacion**: el contenedor Python ejecuta Flask/Gunicorn usando
   `newrelic-admin run-program`. Esto permite medir transacciones web,
   tiempos de respuesta, errores, trazas y llamadas a base de datos.
2. **Monitoreo de AWS/ECS**: New Relic se conecta con AWS mediante la
   integracion de CloudWatch Metric Streams y, para Fargate, puede usarse el
   contenedor sidecar `newrelic-infra` dentro de la task definition.

## Cambios en la aplicacion

- Se agrego la dependencia `newrelic` en `requirements.txt`.
- El proceso web arranca con `newrelic-admin run-program`.
- El `Dockerfile` usa el mismo comando instrumentado para Fargate.
- La licencia y el nombre de la aplicacion se configuran por variables de
  entorno, no en el repositorio.

Variables requeridas en la task de Fargate:

```txt
NEW_RELIC_LICENSE_KEY=<secret>
NEW_RELIC_APP_NAME=blacklist-api
NEW_RELIC_LOG=stdout
```

Variables recomendadas:

```txt
NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
NEW_RELIC_ENVIRONMENT=production
```

## Sidecar recomendado para Fargate

Para obtener metricas del entorno ECS/Fargate, la task definition puede incluir
un segundo contenedor:

```txt
name: newrelic-infra
image: newrelic/nri-ecs:latest
essential: false
```

Ese contenedor debe recibir la licencia de New Relic y la configuracion indicada
por Terraform. El contenedor principal de la API sigue siendo el responsable del
APM de Flask.

## Pipeline esperado

El `buildspec.yml` ejecuta pruebas, construye la imagen Docker, la publica en
ECR y genera artefactos compatibles con despliegue en ECS:

- `imagedefinitions.json`: usado por acciones ECS estandar en CodePipeline.
- `imageDetail.json`: usado comunmente por despliegues ECS blue/green con
  CodeDeploy.

Variables requeridas en CodeBuild:

```txt
ECR_REPOSITORY_URI=<account>.dkr.ecr.<region>.amazonaws.com/<repository>
ECS_CONTAINER_NAME=blacklist-api
```

CodeBuild debe tener modo privilegiado habilitado para poder ejecutar Docker.

## Indicadores a observar

- Tasa de errores 5xx y 4xx.
- Latencia promedio y percentiles altos de `/blacklists`.
- Apdex de la aplicacion.
- Errores no controlados en Flask/Gunicorn.
- Uso de CPU y memoria de la task Fargate.
- Reinicios de contenedores.
- Saturacion o fallos de conexion hacia PostgreSQL.

## Alertas sugeridas

- Error rate mayor a 5% durante 5 minutos.
- Tiempo de respuesta promedio mayor a 1 segundo durante 5 minutos.
- CPU de la task mayor a 80% durante 10 minutos.
- Memoria de la task mayor a 85% durante 10 minutos.
- Cualquier fallo sostenido del endpoint `/health`.

## Resultado esperado

Con esta configuracion, New Relic permite correlacionar una alerta de AWS/ECS
con el detalle interno de la aplicacion: endpoint afectado, excepcion, traza y
tiempo consumido por la base de datos.
