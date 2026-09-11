import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from api.services import (
    _presion_superficie,
    obtener_clima_tramo,
    obtener_referencia_vial,
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


if __name__ == "__main__":
    unittest.main()
