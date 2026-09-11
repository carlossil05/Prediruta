import unittest

from api.utils import (
    densificar_polyline,
    distancia_polyline,
    punto_medio_polyline,
    segmentar_por_zona,
)


class UtilidadesRutaTest(unittest.TestCase):
    def test_densificacion_respeta_separacion_maxima(self):
        puntos = [(4.60, -74.10), (4.60, -74.09)]
        densos = densificar_polyline(puntos, separacion_maxima_m=100)
        self.assertGreater(len(densos), 2)
        self.assertLessEqual(
            max(
                distancia_polyline([inicio, fin])
                for inicio, fin in zip(densos, densos[1:])
            ),
            0.101,
        )

    def test_segmentacion_ocurre_al_cambiar_zona(self):
        def zona(_latitud, longitud):
            return 1 if longitud < -74.095 else 2

        tramos = segmentar_por_zona(
            [(4.60, -74.10), (4.60, -74.09)],
            zona,
            separacion_maxima_m=100,
        )
        self.assertEqual([tramo["zona"] for tramo in tramos], [1, 2])
        self.assertEqual(tramos[0]["puntos"][-1], tramos[1]["puntos"][0])

    def test_punto_medio_se_ubica_sobre_la_ruta(self):
        medio = punto_medio_polyline(
            [(4.60, -74.10), (4.60, -74.09), (4.60, -74.08)]
        )
        self.assertAlmostEqual(medio[0], 4.60, places=5)
        self.assertAlmostEqual(medio[1], -74.09, places=4)


if __name__ == "__main__":
    unittest.main()
