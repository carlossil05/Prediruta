import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import numpy as np

from api.predictors import (
    metadata_estado,
    metadata_ocurrencia,
    predecir_estado_actor,
    predecir_ocurrencia,
)


class ModelosProduccionTest(unittest.TestCase):
    def setUp(self):
        self.momento = datetime(
            2026, 9, 12, 15, 30, tzinfo=ZoneInfo("America/Bogota")
        )

    def test_score_ocurrencia_esta_en_rango(self):
        clima = {
            "temperatura": 18.0,
            "precipitacion": 1.2,
            "nubosidad": 75.0,
            "presion": 750.0,
            "velocidad_viento": 12.0,
            "direccion_viento_sin": 0.0,
            "direccion_viento_cos": 1.0,
        }
        score = predecir_ocurrencia(4, self.momento, clima)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    @patch("api.predictors.modelo_ocurrencia")
    def test_ocurrencia_recibe_el_contrato_completo_con_clima(self, modelo):
        modelo.predict_proba.return_value = np.array([[0.2, 0.8]])
        clima = {
            "temperatura": 18.0, "precipitacion": 1.2, "nubosidad": 75.0,
            "presion": 750.0, "velocidad_viento": 12.0,
            "direccion_viento_sin": 0.0, "direccion_viento_cos": 1.0,
        }

        predecir_ocurrencia(4, self.momento, clima)

        entrada = modelo.predict_proba.call_args.args[0]
        self.assertEqual(list(entrada.columns), metadata_ocurrencia["columnas_entrada"])
        self.assertEqual(entrada.iloc[0]["ZONA_CIUDAD"], 4)
        self.assertEqual(entrada.iloc[0]["PRECIPITACION"], 1.2)
        self.assertEqual(entrada.iloc[0]["PRESION_SUPERFICIE"], 750.0)

    def test_estado_devuelve_las_tres_clases(self):
        perfil = {
            "edad": 35,
            "genero": 2,
            "clase_vehiculo": 13,
            "servicio_vehiculo": 3,
        }
        probabilidades = predecir_estado_actor(
            4.65, -74.10, 4, self.momento, perfil
        )
        self.assertEqual(set(probabilidades), {"HERIDO", "ILESO", "MUERTO"})
        self.assertAlmostEqual(sum(probabilidades.values()), 1.0, places=5)

    @patch("api.predictors.modelo_estado")
    def test_estado_recibe_perfil_ubicacion_y_tiempo(self, modelo):
        modelo.classes_ = np.array([0, 1, 2])
        modelo.predict_proba.return_value = np.array([[0.6, 0.3, 0.1]])
        perfil = {
            "edad": 35, "genero": 2, "clase_vehiculo": 13,
            "servicio_vehiculo": 3,
        }

        predecir_estado_actor(4.65, -74.10, 4, self.momento, perfil)

        entrada = modelo.predict_proba.call_args.args[0]
        self.assertEqual(list(entrada.columns), metadata_estado["columnas_entrada"])
        self.assertEqual(entrada.iloc[0]["EDAD"], 35)
        self.assertEqual(entrada.iloc[0]["GENERO"], 2)
        self.assertEqual(entrada.iloc[0]["CLASE_VEHICULO"], 13)


if __name__ == "__main__":
    unittest.main()
