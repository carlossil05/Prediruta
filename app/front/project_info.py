"""Presentación pública, estática y trazable del proyecto PrediRuta."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


ASSETS = Path(__file__).resolve().parent / "assets" / "project"
REPOSITORIO = "https://github.com/carlossil05/Prediruta"


def _imagen(nombre: str, descripcion: str, pie: str) -> None:
    """Muestra una figura producida por un notebook con contexto accesible."""

    st.image(
        ASSETS / nombre,
        caption=pie,
        width="stretch",
    )
    st.caption(descripcion)


def mostrar_informacion_proyecto() -> None:
    """Explica el proyecto en una lectura continua, sin formularios ni controles."""

    st.markdown(
        """
        <style>
        .project-back,.project-repo{color:#14777a!important;font-size:.82rem;font-weight:750;
          text-decoration:none!important}.project-hero{background:linear-gradient(135deg,#12324b,#176f72);
          border-radius:22px;color:#fff;margin:.8rem 0 1.3rem;padding:1.8rem 2rem}
        .project-kicker{color:#bfe3df;font-size:.72rem;font-weight:850;letter-spacing:.09em;
          text-transform:uppercase}.project-hero h1{color:#fff;font-size:2.2rem;margin:.2rem 0 .45rem}
        .project-hero p{color:#dceced;font-size:1rem;line-height:1.6;margin:0;max-width:900px}
        .project-meta{align-items:center;display:flex;flex-wrap:wrap;gap:.7rem 1.2rem;margin-top:1rem}
        .project-meta span{color:#d5e9e8;font-size:.76rem}.project-meta a{background:#fff;
          border-radius:9px;color:#126d70!important;font-size:.76rem;font-weight:800;padding:.48rem .7rem;
          text-decoration:none!important}.project-lead{color:#405b68;font-size:1rem;line-height:1.7;
          margin:.2rem 0 1.2rem;max-width:1000px}.project-metrics{display:grid;
          grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:.8rem 0 1.5rem}
        .project-metric,.project-card,.stakeholder,.source-card{background:#fff;border:1px solid #dfe8e9;
          border-radius:15px;box-shadow:0 7px 22px rgba(25,55,70,.045);padding:1rem}
        .project-metric b{color:#14777a;display:block;font-size:1.35rem}.project-metric span{
          color:#607581;font-size:.75rem;line-height:1.4}.project-columns{display:grid;
          grid-template-columns:1fr 1fr;gap:1rem;margin:.8rem 0 1.25rem}
        .project-card{color:#526a76;font-size:.84rem;line-height:1.6}.project-card h3,.stakeholder h3,
          .source-card h3{color:#12324b;font-size:1rem;margin:0 0 .35rem}.project-card b{color:#294a5b}
        .stakeholders{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;
          margin:.8rem 0 1.35rem}.stakeholder{color:#536b77;font-size:.78rem;line-height:1.5}
        .stakeholder .role{color:#14777a;font-size:.68rem;font-weight:850;letter-spacing:.05em;
          margin-bottom:.25rem;text-transform:uppercase}.project-flow{display:grid;
          grid-template-columns:repeat(5,minmax(0,1fr));gap:.55rem;margin:1rem 0 1.4rem}
        .project-flow div{background:#fff;border:1px solid #dfe8e9;border-radius:13px;color:#536b77;
          font-size:.76rem;line-height:1.45;padding:.85rem}.project-flow b{color:#12324b;
          display:block;margin-bottom:.25rem}.project-callout{background:#eef5ff;border:1px solid #cad9ef;
          border-radius:13px;color:#435e78;font-size:.86rem;line-height:1.6;margin:.8rem 0 1.2rem;
          padding:.9rem 1rem}.project-callout.warning{background:#fff8e8;border-color:#efd99b;color:#705817}
        .project-source{background:#f4f7f8;border-radius:8px;color:#49616d;font-family:monospace;
          font-size:.7rem;margin-top:.65rem;padding:.45rem .55rem}.decision{border-left:4px solid #14777a}
        .sources{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem;margin:.8rem 0 1.2rem}
        .source-card{color:#536b77;font-size:.79rem;line-height:1.5}.source-card a{color:#14777a!important;
          font-weight:750;text-decoration:none!important}.figure-note{color:#667d88;font-size:.78rem;
          line-height:1.5;margin-top:-.3rem}.project-footer{border-top:1px solid #dfe8e9;color:#607581;
          font-size:.78rem;margin-top:1.7rem;padding-top:1rem}
        @media(max-width:900px){.project-metrics,.stakeholders{grid-template-columns:1fr 1fr}
          .project-flow{grid-template-columns:1fr 1fr}.project-hero{padding:1.3rem}}
        @media(max-width:580px){.project-metrics,.stakeholders,.project-flow,.project-columns,
          .sources{grid-template-columns:1fr}.project-hero h1{font-size:1.75rem}}
        </style>
        <a class="project-back" href="./" target="_self">← Volver a planear una ruta</a>
        <div class="project-hero">
          <div class="project-kicker">Proyecto aplicado en analítica de datos</div>
          <h1>PrediRuta</h1>
          <p>Un sistema informativo que transforma un trayecto futuro dentro de Bogotá
          en una lectura conjunta de criticidad relativa, tiempos de paso y clima previsto.</p>
          <div class="project-meta"><span>Lizeth García · Carlos Silva · Leonardo Guzman</span>
          <a href="https://github.com/carlossil05/Prediruta" target="_blank" rel="noopener">
          Ver repositorio en GitHub ↗</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Por qué existe PrediRuta")
    st.markdown(
        """
        <p class="project-lead">La criticidad vial no se distribuye de manera uniforme
        ni permanece constante durante el día. Una ruta puede cruzar lugares con patrones
        históricos distintos y hacerlo en horas y condiciones meteorológicas diferentes.
        Aunque hoy es posible consultar rutas y clima por separado, esa información no
        explica cómo cambia el contexto de siniestralidad a lo largo del recorrido.</p>
        <div class="project-columns">
          <div class="project-card"><h3>Pregunta del proyecto</h3>¿Cómo estimar la criticidad
          espacio-temporal de los tramos de una ruta en Bogotá a partir de patrones
          históricos de siniestralidad y evaluar el aporte de las condiciones meteorológicas?</div>
          <div class="project-card"><h3>Propuesta de valor</h3>Integrar ruta, hora estimada
          de paso, clima y modelos analíticos en una visualización comprensible antes del viaje.
          El resultado apoya una lectura informada; no selecciona rutas ni da instrucciones.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Para quién puede generar valor")
    st.markdown(
        """
        <div class="stakeholders">
          <div class="stakeholder"><div class="role">Usuario directo</div><h3>Conductores</h3>
          Personas que se desplazan en automóvil o motocicleta y quieren comprender el
          contexto previsto de su recorrido antes de salir.</div>
          <div class="stakeholder"><div class="role">Usuario secundario</div><h3>Movilidad y seguridad vial</h3>
          Equipos que podrían usar resultados agregados por zona y momento para complementar
          diagnósticos, sin hacer seguimiento individual.</div>
          <div class="stakeholder"><div class="role">Actor interesado</div><h3>Gestores de infraestructura</h3>
          Entidades que podrían contrastar patrones recurrentes con operación, señalización
          e infraestructura en estudios posteriores.</div>
          <div class="stakeholder"><div class="role">Usuario secundario</div><h3>Academia</h3>
          Investigadores que necesitan reproducir la preparación de datos, evaluar modelos
          y explorar nuevas variables explicativas.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Qué trabajo hay detrás")
    st.markdown(
        """
        <div class="project-flow">
          <div><b>1 · Calidad</b>Normalización de identificadores, fechas, horas y coordenadas.</div>
          <div><b>2 · Alcance</b>Validación contra el perímetro urbano oficial de Bogotá.</div>
          <div><b>3 · Integración</b>Relaciones entre accidentes, actores, vehículos, vías y clima.</div>
          <div><b>4 · Modelado</b>Escenarios, algoritmos, umbrales y evaluación fuera de tiempo.</div>
          <div><b>5 · Producto</b>Servicios de Google y dos pipelines productivos por tramo.</div>
        </div>
        <div class="project-metrics">
          <div class="project-metric"><b>904.476</b><span>registros iniciales de accidentes</span></div>
          <div class="project-metric"><b>895.346</b><span>accidentes finales después de la depuración</span></div>
          <div class="project-metric"><b>99,04 %</b><span>cumplimiento conjunto de calidad, periodo y perímetro antes del ajuste final</span></div>
          <div class="project-metric"><b>100 %</b><span>eventos elegibles con clima histórico asociado</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columna_anios, columna_zonas = st.columns([0.9, 1.25], gap="large")
    with columna_anios:
        _imagen(
            "accidentes_por_anio.png",
            "La línea de 2007 marca el inicio elegido por cobertura. Las caídas de los "
            "últimos años también reflejan cambios de disponibilidad y no deben leerse "
            "automáticamente como una reducción real de la siniestralidad.",
            "Figura 1. Accidentes registrados por año. Fuente: notebook de limpieza.",
        )
    with columna_zonas:
        _imagen(
            "zonas_geograficas.png",
            "Las 150 zonas ofrecen un compromiso entre detalle espacial, estabilidad "
            "computacional y suficientes observaciones para formar patrones recurrentes.",
            "Figura 2. Distribución y tamaño de las zonas. Fuente: notebook de construcción del dataset.",
        )

    st.markdown("## Diseño de los datos y prevención de fuga")
    st.markdown(
        """
        <div class="project-columns">
          <div class="project-card"><h3>Ocurrencia</h3>Una fila representa
          <b>año + zona + mes + día de la semana + hora</b>. Para cada año completo se
          generan 150 × 12 × 7 × 24 = 302.400 combinaciones. El año define los cortes,
          pero no entra al modelo.</div>
          <div class="project-card"><h3>Estado del actor</h3>Una fila representa un actor
          involucrado en un accidente. Los actores del mismo evento permanecen en la misma
          partición para impedir que un siniestro aparezca a la vez en ajuste y evaluación.</div>
        </div>
        <div class="project-callout">Los modelos se evalúan temporalmente: entrenamiento
        hasta 2020, validación entre 2021 y 2023 y prueba con años posteriores. Esta decisión
        mide mejor la generalización ante cambios reales que una división puramente aleatoria.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Modelo de ocurrencia")
    st.markdown(
        """
        <div class="project-columns">
          <div class="project-card decision"><h3>Selección productiva actual</h3>Se compararon
          regresión logística, Random Forest, XGBoost y MLP bajo escenarios equivalentes.
          El artefacto productivo actual es una <b>MLP con clima</b>: zona, mes, día, hora,
          temperatura, precipitación, nubosidad, presión y viento.</div>
          <div class="project-card"><h3>Resultados fuera de muestra</h3><b>Validación 2021–2023:</b>
          Balanced Accuracy 0,6234 y ROC-AUC 0,6661.<br><b>Prueba 2024–2025:</b>
          Balanced Accuracy 0,5981, ROC-AUC 0,6308 y recall 0,6920. El umbral 0,3090
          se eligió únicamente con validación.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _imagen(
        "comparacion_ocurrencia.png",
        "La selección no depende de accuracy aislada: combina Balanced Accuracy, "
        "ROC-AUC, pérdida probabilística y comportamiento temporal. Average Precision "
        "permanece baja por el fuerte desbalance del objetivo.",
        "Figura 3. Comparación de modelos y escenarios en validación. Fuente: notebook de ocurrencia.",
    )
    st.markdown(
        """
        <div class="project-callout warning"><b>Evolución documentada:</b> la entrega 2
        registró XGBoost sin clima como decisión de esa fase. Después se reconstruyó la
        cuadrícula anual y se repitieron los experimentos. El notebook y los metadatos
        exportados más recientes seleccionan MLP con clima; la aplicación ejecuta ese
        artefacto final. La mejora frente a la misma MLP sin clima es pequeña, por lo que
        el resultado se comunica como score relativo y no como probabilidad individual.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Modelo de estado del actor")
    st.markdown(
        """
        <div class="project-columns">
          <div class="project-card decision"><h3>Selección productiva</h3>El XGBoost
          <b>operativo sin clima</b> estima HERIDO, ILESO o MUERTO si ocurriera un siniestro.
          Usa ubicación, fecha, hora, edad, género, clase y servicio del vehículo.
          “Sin información” se excluye como objetivo porque no es una consecuencia.</div>
          <div class="project-card"><h3>Resultados de prueba 2024–2026</h3>F1 macro 0,5688,
          Balanced Accuracy 0,5926, accuracy 0,7747 y ROC-AUC multiclase 0,8367.
          Supera ampliamente la línea base de F1 macro 0,1578. El clima no produjo una
          mejora consistente en el escenario operativo.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _imagen(
        "comparacion_estado.png",
        "Los escenarios completos funcionan como techo experimental, pero incluyen datos "
        "que no existen antes del viaje. Por eso producción utiliza el escenario operativo.",
        "Figura 4. Modelos de estado por alcance y disponibilidad de clima. Fuente: notebook de estado.",
    )
    columna_matriz, columna_lectura = st.columns([1.05, 0.95], gap="large")
    with columna_matriz:
        _imagen(
            "matriz_estado.png",
            "El modelo reconoce aproximadamente 79 % de HERIDO e ILESO, pero solo 21 % "
            "de MUERTO; la mayoría de esos casos se confunde con HERIDO. Esta limitación "
            "justifica mostrar la distribución completa y no una afirmación determinista.",
            "Figura 5. Matriz de confusión normalizada en prueba temporal.",
        )
    with columna_lectura:
        st.markdown(
            """
            <div class="project-card"><h3>Por qué el estado es condicional</h3>Este segundo
            modelo no calcula si el accidente ocurrirá. Solo se consulta en los tramos de
            mayor score y responde una pregunta distinta: <b>si hubiera un siniestro bajo
            este contexto y perfil, ¿qué estado sería más compatible con los datos?</b><br><br>
            Mostrar HERIDO, ILESO y MUERTO simultáneamente evita ocultar la incertidumbre
            y permite observar las clases minoritarias.</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## De los modelos al mapa")
    st.markdown(
        """
        1. Google Routes calcula la geometría y el tiempo con tráfico.
        2. El recorrido cambia de tramo al cruzar una de las 150 zonas del entrenamiento.
        3. Google calcula el tiempo específico para cada tramo delimitado.
        4. Google Weather consulta el clima para el punto y la hora representativos.
        5. Las variables entran directamente al pipeline MLP de ocurrencia.
        6. Los scores se comparan con el umbral validado y se ordenan dentro de la ruta.
        7. En los tres tramos prioritarios se ejecuta el XGBoost de estado del actor.
        """
    )

    st.markdown("## Alcance y límites")
    st.markdown(
        """
        <div class="project-callout warning"><b>PrediRuta es descriptivo y predictivo,
        no prescriptivo.</b> No recomienda rutas, no emite instrucciones de conducción,
        no afirma causalidad entre clima y siniestros y no identifica una probabilidad
        individual. Un tramo verde tampoco significa “seguro”: expresa una comparación
        relativa con la evidencia histórica y con los demás tramos del recorrido.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Fuentes y trazabilidad")
    st.markdown(
        """
        <div class="sources">
          <div class="source-card"><h3>Siniestralidad vial</h3>Tablas históricas de
          ACCIDENTE, ACTOR_VIAL, VEHICULO, VIA y CAUSA.<br>
          <a href="https://datos.movilidadbogota.gov.co/" target="_blank" rel="noopener">
          Portal de Datos de la Secretaría Distrital de Movilidad ↗</a></div>
          <div class="source-card"><h3>Perímetro urbano</h3>Límite oficial usado para
          definir la cobertura espacial del proyecto.<br>
          <a href="https://datosabiertos.bogota.gov.co/dataset/perimetro-urbano-bogota-d-c"
          target="_blank" rel="noopener">Secretaría Distrital de Planeación ↗</a></div>
          <div class="source-card"><h3>Clima histórico</h3>ERA5 y ECMWF IFS consultados
          durante la construcción de las variables meteorológicas.<br>
          <a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank"
          rel="noopener">Open-Meteo Historical Weather API ↗</a></div>
          <div class="source-card"><h3>Operación del prototipo</h3>Google Routes aporta
          la ruta y los tiempos; Google Weather aporta el pronóstico horario.<br>
          <a href="https://developers.google.com/maps/documentation/routes" target="_blank"
          rel="noopener">Google Routes ↗</a> ·
          <a href="https://developers.google.com/maps/documentation/weather" target="_blank"
          rel="noopener">Google Weather ↗</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="project-footer">Documentación reproducible en los notebooks
        <code>data/limpieza_estructuracion_bd.ipynb</code>,
        <code>data/construccion_dataset.ipynb</code>,
        <code>modelo/modelo_ocurrencia_accidente.ipynb</code> y
        <code>modelo/modelo_estado_victima.ipynb</code>.<br><br>
        <a class="project-repo" href="{REPOSITORIO}" target="_blank" rel="noopener">
        Explorar el código, notebooks y artefactos en GitHub ↗</a></div>
        """,
        unsafe_allow_html=True,
    )
