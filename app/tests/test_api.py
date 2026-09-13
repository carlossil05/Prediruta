import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from fastapi import HTTPException

from api.api import (
    UMBRAL_MODELO_OCURRENCIA,
    app,
    construir_ubicaciones_tramos,
    validar_cobertura_bogota,
    validar_horizonte,
)


class ContratoApiTest(unittest.TestCase):
    def setUp(self):
        self.cliente = TestClient(app)

    def test_health_informa_los_dos_modelos(self):
        respuesta = self.cliente.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            set(respuesta.json()["modelos"]), {"ocurrencia", "estado_actor"}
        )

    def test_rechaza_consulta_sin_consentimiento(self):
        payload = self._payload()
        payload["consentimiento_datos"] = False
        respuesta = self.cliente.post("/predict", json=payload)
        self.assertEqual(respuesta.status_code, 422)

    @patch("api.api.datetime")
    def test_acepta_el_minuto_actual_como_hora_de_salida(self, reloj):
        salida = datetime(2026, 9, 13, 10, 43, tzinfo=ZoneInfo("America/Bogota"))
        reloj.now.return_value = salida + timedelta(seconds=42)

        validar_horizonte(salida)

    @patch("api.api.datetime")
    def test_rechaza_un_minuto_que_ya_paso(self, reloj):
        salida = datetime(2026, 9, 13, 10, 42, tzinfo=ZoneInfo("America/Bogota"))
        reloj.now.return_value = datetime(
            2026, 9, 13, 10, 43, 1, tzinfo=ZoneInfo("America/Bogota")
        )

        with self.assertRaises(HTTPException) as contexto:
            validar_horizonte(salida)

        self.assertIn("no puede estar en el pasado", str(contexto.exception.detail))

    @patch("api.api.obtener_ruta_base_google")
    def test_rechaza_origen_fuera_de_cobertura_antes_de_consultar_google(
        self, ruta
    ):
        payload = self._payload()
        payload["origen_coordenadas"] = {
            "latitud": 4.95,
            "longitud": -74.10,
        }

        respuesta = self.cliente.post("/predict", json=payload)

        self.assertEqual(respuesta.status_code, 422)
        self.assertIn("fuera del área urbana de Bogotá", respuesta.text)
        ruta.assert_not_called()

    @patch("api.api.distancia_centroide_mas_cercano_km")
    def test_revisa_todos_los_puntos_de_una_ruta(self, distancia):
        distancia.side_effect = [0.2, 0.5, 3.1, 0.4]
        tramos = [
            {
                "puntos": [
                    (4.70, -74.10),
                    (4.72, -74.12),
                    (4.78, -74.16),
                    (4.71, -74.11),
                ]
            }
        ]

        with self.assertRaises(HTTPException) as contexto:
            validar_cobertura_bogota(tramos)

        self.assertIn("sale del área urbana", str(contexto.exception.detail))
        self.assertEqual(distancia.call_count, 4)

    @patch("api.api.validar_cobertura_bogota")
    @patch("api.api.predecir_estado_actor")
    @patch("api.api.predecir_ocurrencia")
    @patch("api.api.obtener_clima_tramo")
    @patch("api.api.obtener_tiempos_google_por_tramo")
    @patch("api.api.segmentar_por_zona")
    @patch("api.api.obtener_ruta_base_google")
    def test_estado_solo_aparece_en_tramo_detectado_prioritario(
        self,
        ruta,
        segmentacion,
        tiempos,
        clima,
        ocurrencia,
        estado,
        _cobertura,
    ):
        ruta.return_value = {
            "polyline": "_gjaF~dwtM?_pR",
            "distancia_m": 1000,
            "duracion_s": 600,
            "inicio": {"latitude": 4.60, "longitude": -74.10},
            "fin": {"latitude": 4.60, "longitude": -74.09},
            "advertencias": [],
            "proveedor": "routes_v2",
        }
        segmentacion.return_value = [
            {"zona": 7, "puntos": [(4.60, -74.10), (4.60, -74.09)]}
        ]
        tiempos.return_value = [{"duracion_s": 600, "distancia_m": 1000}]
        clima.return_value = {
            "temperatura": 18.0,
            "precipitacion": 0.0,
            "nubosidad": 50.0,
            "presion": 750.0,
            "velocidad_viento": 8.0,
            "direccion_viento_grados": 0.0,
            "direccion_viento_sin": 0.0,
            "direccion_viento_cos": 1.0,
            "hora_pronostico": "2026-09-11T12:00",
            "condicion": "Nublado",
            "probabilidad_precipitacion": 10.0,
            "modelo": "Google Weather API",
            "latitud_modelo": 4.60,
            "longitud_modelo": -74.10,
        }
        ocurrencia.return_value = 0.75
        estado.return_value = {"HERIDO": 0.6, "ILESO": 0.3, "MUERTO": 0.1}

        respuesta = self.cliente.post("/predict", json=self._payload())
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        tramo = respuesta.json()["tramos"][0]
        self.assertEqual(tramo["nivel_criticidad"], "Alto")
        self.assertIsNotNone(tramo["estado_actor"])
        estado.assert_called_once()

        ocurrencia.return_value = UMBRAL_MODELO_OCURRENCIA - 0.01
        estado.reset_mock()
        respuesta = self.cliente.post("/predict", json=self._payload())
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertIsNone(respuesta.json()["tramos"][0]["estado_actor"])
        estado.assert_not_called()

    @patch("api.api.obtener_referencia_vial")
    def test_todos_los_tramos_informan_desde_y_hasta(self, referencia):
        referencias = {
            (4.71, -74.09): "Calle 80, Engativá",
            (4.72, -74.08): "Carrera 30, Barrios Unidos",
        }
        referencia.side_effect = lambda latitud, longitud: referencias[
            (latitud, longitud)
        ]
        contextos = [
            {
                "puntos": [
                    (4.70000, -74.10000),
                    (4.71000, -74.09000),
                ]
            },
            {
                "puntos": [
                    (4.71000, -74.09000),
                    (4.72000, -74.08000),
                ]
            },
            {
                "puntos": [
                    (4.72000, -74.08000),
                    (4.73000, -74.07000),
                ]
            },
        ]

        ubicaciones = construir_ubicaciones_tramos(
            contextos, "Portal Norte, Bogotá", "Universidad de los Andes, Bogotá"
        )

        self.assertEqual(
            ubicaciones,
            [
                {
                    "desde": "Portal Norte, Bogotá",
                    "hasta": "Calle 80, Engativá",
                },
                {
                    "desde": "Calle 80, Engativá",
                    "hasta": "Carrera 30, Barrios Unidos",
                },
                {
                    "desde": "Carrera 30, Barrios Unidos",
                    "hasta": "Universidad de los Andes, Bogotá",
                },
            ],
        )

    @patch("api.api.validar_cobertura_bogota")
    @patch("api.api.predecir_estado_actor")
    @patch("api.api.predecir_ocurrencia")
    @patch("api.api.obtener_clima_tramo")
    @patch("api.api.obtener_referencia_vial", return_value="Calle 80, Engativá")
    @patch("api.api.obtener_tiempos_google_por_tramo")
    @patch("api.api.segmentar_por_zona")
    @patch("api.api.obtener_ruta_base_google")
    def test_hora_de_llegada_google_alimenta_clima_y_modelo_por_tramo(
        self,
        ruta,
        segmentacion,
        tiempos,
        _referencia,
        clima,
        ocurrencia,
        estado,
        _cobertura,
    ):
        ruta.return_value = {
            "polyline": "_gjaF~dwtM?_pR",
            "distancia_m": 2100,
            # La segunda consulta puede repartir una duración distinta; la ETA
            # autoritativa de la ruta principal debe conservarse.
            "duracion_s": 900,
            "inicio": {"latitude": 4.60, "longitude": -74.10},
            "fin": {"latitude": 4.62, "longitude": -74.08},
            "advertencias": [],
            "proveedor": "routes_v2",
        }
        segmentacion.return_value = [
            {"zona": 7, "puntos": [(4.60, -74.10), (4.61, -74.09)]},
            {"zona": 8, "puntos": [(4.61, -74.09), (4.62, -74.08)]},
        ]
        tiempos.return_value = [
            {"duracion_s": 300, "distancia_m": 900},
            {"duracion_s": 420, "distancia_m": 1200},
        ]
        clima.side_effect = lambda _lat, _lng, momento: {
            "temperatura": 18.0,
            "precipitacion": 0.0,
            "nubosidad": 50.0,
            "presion": 750.0,
            "velocidad_viento": 8.0,
            "direccion_viento_grados": 0.0,
            "direccion_viento_sin": 0.0,
            "direccion_viento_cos": 1.0,
            "hora_pronostico": momento.isoformat(),
            "condicion": "Nublado",
            "probabilidad_precipitacion": 10.0,
            "modelo": "Google Weather API",
            "latitud_modelo": _lat,
            "longitud_modelo": _lng,
        }
        ocurrencia.return_value = UMBRAL_MODELO_OCURRENCIA - 0.01

        payload = self._payload()
        salida = datetime.combine(
            datetime.fromisoformat(payload["fecha_salida"]).date(),
            datetime.strptime(payload["hora_salida"], "%H:%M").time(),
            tzinfo=ZoneInfo("America/Bogota"),
        )
        respuesta = self.cliente.post("/predict", json=payload)

        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        contenido = respuesta.json()
        tramos = contenido["tramos"]
        llegadas = [
            salida + timedelta(seconds=375),
            salida + timedelta(minutes=15),
        ]
        self.assertEqual(contenido["resumen"]["duracion_estimada"], "15 min")
        self.assertEqual(
            [datetime.fromisoformat(tramo["hora_modelo"]) for tramo in tramos],
            llegadas,
        )
        self.assertEqual(
            [llamada.args[1] for llamada in ocurrencia.call_args_list], llegadas
        )
        self.assertEqual(
            sorted(llamada.args[2] for llamada in clima.call_args_list), llegadas
        )
        self.assertEqual(
            tramos[0]["ubicacion_tramo"],
            {
                "desde": payload["origen"],
                "hasta": "Calle 80, Engativá",
            },
        )
        self.assertEqual(
            tramos[1]["ubicacion_tramo"],
            {
                "desde": "Calle 80, Engativá",
                "hasta": payload["destino"],
            },
        )
        estado.assert_not_called()

    @staticmethod
    def _payload():
        salida = datetime.now(ZoneInfo("America/Bogota")) + timedelta(hours=2)
        return {
            "origen": "Terminal del Sur, Bogotá",
            "destino": "Parque de la 93, Bogotá",
            "fecha_salida": salida.date().isoformat(),
            "hora_salida": salida.strftime("%H:%M"),
            "perfil_actor": {
                "edad": 35,
                "genero": 2,
                "clase_vehiculo": 13,
                "servicio_vehiculo": 3,
            },
            "consentimiento_datos": True,
        }


if __name__ == "__main__":
    unittest.main()
