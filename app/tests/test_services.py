import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from api.services import (
    _consultar_google_routes,
    _presion_superficie,
    ajustar_tiempos_a_duracion_total,
    obtener_clima_tramo,
    obtener_referencia_vial,
    obtener_tiempos_google_por_tramo,
)


class GoogleWeatherTest(unittest.TestCase):
    def test_convierte_presion_a_escala_superficial_del_modelo(self):
        presion = _presion_superficie(1015.0, 14.0, 2553.0)
        self.assertAlmostEqual(presion, 749.1, places=1)

    @patch("api.services._consultar_pronostico_google")
    def test_traduce_respuesta_google_al_contrato_del_modelo(self, consultar):
        consultar.return_value = [
            {
                "interval": {"startTime": "2026-09-10T17:00:00Z"},
                "weatherCondition": {
                    "description": {"text": "Lluvia ligera"}
                },
                "temperature": {"degrees": 14.0, "unit": "CELSIUS"},
                "precipitation": {
                    "probability": {"percent": 70},
                    "qpf": {"quantity": 1.2, "unit": "MILLIMETERS"},
                },
                "airPressure": {"meanSeaLevelMillibars": 1015.0},
                "wind": {
                    "direction": {"degrees": 90},
                    "speed": {"value": 12.0, "unit": "KILOMETERS_PER_HOUR"},
                },
                "cloudCover": 85,
            }
        ]

        clima = obtener_clima_tramo(
            4.674868,
            -74.11331,
            datetime(2026, 9, 10, 12, 20, tzinfo=ZoneInfo("America/Bogota")),
        )

        self.assertEqual(clima["modelo"], "Google Weather API")
        self.assertEqual(clima["condicion"], "Lluvia ligera")
        self.assertEqual(clima["precipitacion"], 1.2)
        self.assertEqual(clima["probabilidad_precipitacion"], 70.0)
        self.assertAlmostEqual(clima["presion"], 749.8, places=1)
        self.assertAlmostEqual(clima["direccion_viento_sin"], 1.0, places=5)

    @patch.dict("os.environ", {"GOOGLE_APIKEY": "clave-prueba"})
    @patch("api.services.requests.get")
    def test_geocodificacion_construye_referencia_vial(self, get):
        obtener_referencia_vial.cache_clear()
        get.return_value.ok = True
        get.return_value.json.return_value = {
            "status": "OK",
            "results": [{
                "formatted_address": "Autopista Norte # 170, Bogotá, Colombia",
                "address_components": [
                    {"long_name": "Autopista Norte", "types": ["route"]},
                    {"long_name": "Usaquén", "types": ["sublocality_level_1"]},
                ],
            }],
        }

        referencia = obtener_referencia_vial(4.75, -74.04)

        self.assertEqual(referencia, "Autopista Norte, Usaquén")


class GoogleRoutesPorTramoTest(unittest.TestCase):
    @patch.dict("os.environ", {"GOOGLE_APIKEY": "clave-prueba"})
    @patch("api.services.requests.post")
    def test_solicita_el_escenario_pesimista_de_trafico(self, post):
        post.return_value.ok = True
        post.return_value.json.return_value = {
            "routes": [{"duration": "3900s", "legs": []}]
        }
        salida = datetime.now(ZoneInfo("America/Bogota")) + timedelta(days=1)

        _consultar_google_routes(
            {"address": "Portal Norte, Bogotá"},
            {"address": "BBVA Calle 72, Bogotá"},
            salida,
        )

        cuerpo = post.call_args.kwargs["json"]
        self.assertEqual(cuerpo["routingPreference"], "TRAFFIC_AWARE_OPTIMAL")
        self.assertEqual(cuerpo["trafficModel"], "PESSIMISTIC")
        self.assertIn("departureTime", cuerpo)

    @patch.dict("os.environ", {"GOOGLE_APIKEY": "clave-prueba"})
    @patch("api.services.requests.post")
    def test_usa_el_instante_de_la_solicitud_para_el_minuto_actual(self, post):
        post.return_value.ok = True
        post.return_value.json.return_value = {
            "routes": [{"duration": "1200s", "legs": []}]
        }
        salida = datetime.now(ZoneInfo("America/Bogota")).replace(
            second=0, microsecond=0
        )

        _consultar_google_routes(
            {"address": "Portal Norte, Bogotá"},
            {"address": "BBVA Calle 72, Bogotá"},
            salida,
        )

        cuerpo = post.call_args.kwargs["json"]
        self.assertNotIn("departureTime", cuerpo)

    def test_ajusta_los_tramos_a_la_eta_de_la_ruta_principal(self):
        tiempos = [
            {"duracion_s": 600.0, "distancia_m": 1000},
            {"duracion_s": 1200.0, "distancia_m": 2000},
        ]

        ajustados = ajustar_tiempos_a_duracion_total(tiempos, 5400.0)

        self.assertEqual(
            [item["duracion_s"] for item in ajustados], [1800.0, 3600.0]
        )
        self.assertEqual(sum(item["duracion_s"] for item in ajustados), 5400.0)
        self.assertEqual(
            [item["distancia_m"] for item in ajustados], [1000, 2000]
        )

    @patch("api.services._consultar_google_routes")
    def test_envia_limites_de_cluster_y_conserva_un_leg_por_tramo(self, consultar):
        salida = datetime(2026, 9, 12, 17, 0, tzinfo=ZoneInfo("America/Bogota"))
        tramos = [
            {"puntos": [(4.60, -74.10), (4.61, -74.09)]},
            {"puntos": [(4.61, -74.09), (4.62, -74.08)]},
            {"puntos": [(4.62, -74.08), (4.63, -74.07)]},
        ]
        consultar.return_value = {
            "legs": [
                {"duration": "300s", "distanceMeters": 900},
                {"duration": "420s", "distanceMeters": 1200},
                {"duration": "180s", "distanceMeters": 700},
            ]
        }

        tiempos = obtener_tiempos_google_por_tramo(tramos, salida)

        self.assertEqual(
            tiempos,
            [
                {"duracion_s": 300.0, "distancia_m": 900},
                {"duracion_s": 420.0, "distancia_m": 1200},
                {"duracion_s": 180.0, "distancia_m": 700},
            ],
        )
        origen, destino, momento, intermedios = consultar.call_args.args
        self.assertEqual(
            origen["location"]["latLng"],
            {"latitude": 4.60, "longitude": -74.10},
        )
        self.assertEqual(
            destino["location"]["latLng"],
            {"latitude": 4.63, "longitude": -74.07},
        )
        self.assertEqual(momento, salida)
        self.assertEqual(
            [punto["location"]["latLng"] for punto in intermedios],
            [
                {"latitude": 4.61, "longitude": -74.09},
                {"latitude": 4.62, "longitude": -74.08},
            ],
        )


if __name__ == "__main__":
    unittest.main()
