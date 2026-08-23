CREATE TABLE "ACCIDENTE" (
  "ACCIDENTE_ID" varchar PRIMARY KEY,
  "FORMULARIO" varchar UNIQUE NOT NULL,
  "FECHA_HORA" timestamp NOT NULL,
  "LATITUD" decimal(9,6) NOT NULL,
  "LONGITUD" decimal(9,6) NOT NULL,
  "DIRECCION" varchar,
  "GRAVEDAD" varchar,
  "CLASE_ACCIDENTE" varchar,
  "LOCALIDAD" varchar,
  "BARRIO" varchar,
  "CIV" varchar,
  "PK_CALZADA" varchar,
  "VIA_CERCANA" varchar,
  "DISTANCIA_VIA" decimal,
  "CLIMA_ID" varchar,
  "ANIO" integer NOT NULL,
  "MES" integer NOT NULL,
  "DIA_SEMANA" integer NOT NULL,
  "HORA" integer NOT NULL,
  "ES_FIN_SEMANA" boolean NOT NULL,
  "OBJETIVO_GRAVE" boolean NOT NULL
);

CREATE TABLE "VIA" (
  "ACCIDENTE_ID" varchar PRIMARY KEY,
  "CODIGO_VIA" varchar,
  "GEOMETRIA_PLANTA" varchar,
  "GEOMETRIA_TERRENO" varchar,
  "GEOMETRIA_SECCION" varchar,
  "SENTIDO_VIA" varchar,
  "N_CALZADAS" integer,
  "N_CARRILES" integer,
  "SUPERFICIE_RODADURA" varchar,
  "ESTADO_VIA" varchar,
  "CONDICION_VIA" varchar,
  "ILUMINACION_ARTIFICIAL" varchar,
  "SEMAFORO" varchar,
  "VISIBILIDAD_VIA" varchar
);

CREATE TABLE "CLIMA" (
  "CLIMA_ID" varchar PRIMARY KEY,
  "FECHA_HORA_CLIMA" timestamp NOT NULL,
  "LATITUD_CELDA" decimal(9,6) NOT NULL,
  "LONGITUD_CELDA" decimal(9,6) NOT NULL,
  "LATITUD_MODELO" decimal(9,6) NOT NULL,
  "LONGITUD_MODELO" decimal(9,6) NOT NULL,
  "ELEVACION_MODELO_M" decimal,
  "TEMPERATURA_2M" decimal,
  "HUMEDAD_RELATIVA_2M" decimal,
  "SENSACION_TERMICA" decimal,
  "PRECIPITACION" decimal,
  "LLUVIA" decimal,
  "CODIGO_CLIMA" integer,
  "NUBOSIDAD" decimal,
  "PRESION_SUPERFICIE" decimal,
  "VELOCIDAD_VIENTO_10M" decimal,
  "DIRECCION_VIENTO_10M" decimal,
  "MODELO" varchar NOT NULL,
  "FUENTE" varchar NOT NULL
);

CREATE TABLE "VEHICULO" (
  "ACCIDENTE_ID" varchar NOT NULL,
  "CODIGO_VEHICULO" varchar NOT NULL,
  "CLASE" varchar,
  "SERVICIO" varchar,
  PRIMARY KEY ("ACCIDENTE_ID", "CODIGO_VEHICULO")
);

CREATE TABLE "ACTOR_VIAL" (
  "ACCIDENTE_ID" varchar NOT NULL,
  "CODIGO_ACTOR" varchar NOT NULL,
  "CODIGO_VEHICULO" varchar,
  "CONDICION" varchar,
  "ESTADO" varchar,
  "GENERO" varchar,
  "EDAD" integer,
  PRIMARY KEY ("ACCIDENTE_ID", "CODIGO_ACTOR")
);

CREATE TABLE "CAUSA" (
  "ACCIDENTE_ID" varchar NOT NULL,
  "CODIGO_VEHICULO" varchar,
  "CODIGO_CAUSA" varchar NOT NULL,
  "NOMBRE" varchar,
  "TIPO" varchar
);

CREATE UNIQUE INDEX ON "CAUSA" ("ACCIDENTE_ID", "CODIGO_VEHICULO", "CODIGO_CAUSA");

COMMENT ON TABLE "ACCIDENTE" IS 'Una fila por accidente válido dentro del alcance definido para PrediRuta.';

COMMENT ON TABLE "VIA" IS 'Una vía representativa por accidente, seleccionada mediante una regla determinística.';

COMMENT ON TABLE "CLIMA" IS 'Una observación meteorológica única por modelo, ubicación y hora. Se utiliza ERA5 antes de 2017 y ECMWF IFS desde 2017.';

COMMENT ON TABLE "VEHICULO" IS 'Vehículos asociados a los accidentes utilizables. La placa no se conserva.';

COMMENT ON TABLE "ACTOR_VIAL" IS 'Actores asociados a los accidentes utilizables de forma anonimizada.';

COMMENT ON TABLE "CAUSA" IS 'Causas asociadas al accidente o a uno de sus vehículos.';

ALTER TABLE "VIA" ADD FOREIGN KEY ("ACCIDENTE_ID") REFERENCES "ACCIDENTE" ("ACCIDENTE_ID") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ACCIDENTE" ADD FOREIGN KEY ("CLIMA_ID") REFERENCES "CLIMA" ("CLIMA_ID") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "VEHICULO" ADD FOREIGN KEY ("ACCIDENTE_ID") REFERENCES "ACCIDENTE" ("ACCIDENTE_ID") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ACTOR_VIAL" ADD FOREIGN KEY ("ACCIDENTE_ID") REFERENCES "ACCIDENTE" ("ACCIDENTE_ID") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "CAUSA" ADD FOREIGN KEY ("ACCIDENTE_ID") REFERENCES "ACCIDENTE" ("ACCIDENTE_ID") DEFERRABLE INITIALLY IMMEDIATE;
