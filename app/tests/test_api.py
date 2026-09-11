import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from fastapi import HTTPException

from api.api import UMBRAL_MODELO_OCURRENCIA, app, validar_cobertura_bogota


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
    def test_estado_solo_aparece_en_sector_detectado_prioritario(
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
