"""Interfaz visual de PrediRuta basada en los mockups de la entrega 1."""

from __future__ import annotations

import html
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st
from dotenv import load_dotenv

from google_maps_components import (
    mostrar_mapa_previo,
    mostrar_mapa_resultado,
    seleccionar_lugar,
)
from project_info import BRAND_ICON, icono_marca, mostrar_informacion_proyecto


# En local se lee app/.env. En despliegue estas variables llegan del entorno.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")
GOOGLE_API_KEY = os.getenv("GOOGLE_APIKEY", "")
# Las claves específicas tienen prioridad. Si no existen, la clave general
# mantiene operativo el prototipo tanto en local como en Railway.
PLACES_API_KEY = os.getenv("GOOGLE_PLACES_APIKEY", "") or GOOGLE_API_KEY
MAPS_BROWSER_KEY = os.getenv("GOOGLE_MAPS_BROWSER_KEY", "") or GOOGLE_API_KEY

ZONA_BOGOTA = ZoneInfo("America/Bogota")
DIAS_PRONOSTICO = 7

# Correspondencia exacta con DICCIONARIO_CATEGORIAS. Las etiquetas se adaptan
# al lenguaje del usuario, pero el modelo siempre recibe el código original.
GENEROS = {
    "Prefiero no decirlo": 0,  # SIN INFORMACION
    "Femenino": 1,
    "Masculino": 2,
}
CLASES_VEHICULO = {"Automóvil": 1, "Motocicleta": 13}
SERVICIOS_VEHICULO = {
    "Sin información": 0,
    "Diplomático": 1,
    "Oficial": 2,
    "Particular": 3,
    "Público": 4,
}


st.set_page_config(
    page_title="PrediRuta | Analiza la criticidad de cada tramo de tu recorrido",
    page_icon=str(BRAND_ICON),
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
      --navy:#12324b; --teal:#14777a; --teal-dark:#0f676a;
      --muted:#607581; --muted-soft:#788b95; --line:#dbe6e8;
      --surface:#ffffff; --surface-soft:#f5faf9; --blue-soft:#eef6ff;
      --radius:16px; --radius-inner:11px;
      --shadow:0 10px 28px rgba(25,55,70,.065);
      --text-display:clamp(1.9rem,2.05vw,2.2rem);
      --text-heading:clamp(1.05rem,1.08vw,1.16rem);
      --text-body:clamp(.84rem,.82vw,.9rem);
      --text-small:clamp(.72rem,.7vw,.77rem);
    }
    html,body,#root,[data-testid="stAppViewContainer"] {
      background:#fcfefe!important;color-scheme:light;margin:0!important;padding:0!important;
    }
    .stApp {background:linear-gradient(180deg,#fcfefe 0%,#f1f8fa 100%);}
    header[data-testid="stHeader"],[data-testid="stDecoration"],[data-testid="stToolbar"]{
      display:none!important;height:0!important;min-height:0!important;
    }
    [data-testid="stMain"],.main {padding-top:0!important;top:0!important;}
    .block-container {max-width:1600px;padding:.6rem 2rem 3rem;position:relative;z-index:1;}
    #MainMenu,footer {display:none!important;}
    [data-testid="stVerticalBlock"] {gap:.65rem;}
    h1,h2,h3,h4 {color:var(--navy);letter-spacing:-.025em;line-height:1.2;}
    h2{font-size:1.5rem!important} h3{font-size:var(--text-heading)!important}
    h4{font-size:var(--text-body)!important}
    p,li,[data-testid="stMarkdownContainer"] {font-size:var(--text-body);}

    /* Identidad y cabecera */
    .predi-brand {align-items:center;display:flex;gap:.85rem;margin:0 0 .25rem;}
    .predi-logo {align-items:center;background:linear-gradient(145deg,#16878a,#0f6467);
      border-radius:14px;box-shadow:0 8px 20px rgba(20,119,122,.2);color:#fff;
      display:flex;flex:0 0 56px;height:56px;justify-content:center;width:56px;}
    .predi-logo img{border-radius:inherit;display:block;height:100%;object-fit:cover;width:100%}
    .predi-title {color:var(--navy);font-size:var(--text-display);font-weight:800;
      letter-spacing:-.045em;line-height:1.08;}
    .predi-subtitle {color:var(--muted);font-size:var(--text-body);line-height:1.45;
      margin:0 0 .9rem 4.45rem;}
    .hero-art{height:170px;opacity:.9;pointer-events:none;position:absolute;right:0;
      top:0;width:82%;z-index:-1;overflow:hidden}
    .hero-art svg{display:block;height:100%;width:100%}
    .ui-icon{display:block;height:20px;stroke:currentColor;stroke-linecap:round;
      stroke-linejoin:round;stroke-width:1.8;width:20px}

    /* Navegación y mensajes */
    .method-link {align-items:center;background:rgba(255,255,255,.96);border:1px solid var(--line);
      border-radius:var(--radius-inner);color:var(--teal)!important;display:flex;
      font-size:var(--text-body);font-weight:750;justify-content:center;margin-top:.25rem;
      min-height:44px;padding:.2rem .8rem;text-decoration:none!important;transition:.15s ease;}
    .method-link:hover {background:#eef7f6;border-color:#bcd8d6;}
    .hero-motto{color:#145875;font-family:Georgia,serif;font-size:.82rem;font-style:italic;
      line-height:1.2;margin:.35rem .7rem 0 0;text-align:right;transform:rotate(-3deg)}
    .feature-ribbon{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin:.15rem 0 .9rem}
    .feature-chip{align-items:center;background:rgba(255,255,255,.95);border:1px solid var(--line);
      border-radius:var(--radius);box-shadow:var(--shadow);display:grid;
      grid-template-columns:50px 1fr;gap:.8rem;min-height:82px;padding:.7rem 1rem}
    .feature-icon,.panel-icon,.summary-icon{align-items:center;background:#e6f3f2;
      border-radius:50%;color:var(--teal);display:flex;justify-content:center}
      .feature-icon{height:50px;width:50px}.feature-icon .ui-icon{height:27px;width:27px}.feature-chip b{color:var(--navy);display:block;
      font-size:var(--text-body);line-height:1.25}.feature-chip>div:last-child>span{color:var(--muted);
      display:block;font-size:var(--text-small);line-height:1.4;margin-top:.15rem}

    /* Paneles y formulario */
    div[data-testid="stVerticalBlockBorderWrapper"] {background:rgba(255,255,255,.97);
      border-color:var(--line)!important;border-radius:var(--radius);box-shadow:var(--shadow);}
    .panel-title {align-items:center;display:flex;gap:.8rem;margin-bottom:.6rem;min-height:50px;}
    .panel-icon {flex:0 0 48px;height:48px;width:48px;}
    .map-title .panel-icon{background:linear-gradient(145deg,#16878a,#0f6467);color:#fff}
    .panel-title strong {color:var(--navy);display:block;font-size:var(--text-heading);line-height:1.25;}
    .panel-title span {color:var(--muted);display:block;font-size:var(--text-body);
      line-height:1.4;margin-top:.12rem;}
    .panel-tag{background:#f3f8f8;border:1px solid var(--line);border-radius:10px;color:var(--teal);
      float:right;font-size:var(--text-small);font-weight:750;padding:.42rem .65rem}
    .panel-tag::before{background:var(--teal);border-radius:50%;content:'';display:inline-block;
      height:6px;margin-right:.35rem;vertical-align:middle;width:6px}
    [data-testid="stWidgetLabel"] p{color:var(--navy)!important;font-size:var(--text-body)!important;
      font-weight:750!important;line-height:1.25!important}
    /* El autocompletado conserva su espacio cerrado; al abrirse, la lista crece
       sobre el formulario y no empuja la fecha ni los controles siguientes. */
    div[data-testid="stElementContainer"]:has(iframe[title="streamlit_searchbox.searchbox"]){
      min-height:76px;overflow:visible;position:relative;z-index:20}
    iframe[title="streamlit_searchbox.searchbox"]{left:0;position:absolute!important;
      top:0;width:100%;z-index:50!important}
    [data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="base-input"]{
      background:#fff!important;border-color:#d5e1e5!important;border-radius:var(--radius-inner)!important;
      color:var(--navy)!important;min-height:42px!important}
    [data-baseweb="input"] input,[data-baseweb="select"] *{font-size:var(--text-body)!important}
    input{color:var(--navy)!important}
    [data-testid="stCheckbox"] label p,[data-testid="stCaptionContainer"] p,
    [data-testid="stAlertContainer"] p{font-size:var(--text-small)!important;line-height:1.45!important}
    .info-strip,.why-card{background:var(--blue-soft);border:1px solid #cadff4;
      border-radius:var(--radius-inner);color:#42627e;font-size:var(--text-small);
      line-height:1.45;padding:.65rem .75rem}
    .info-strip{align-items:center;display:grid;gap:.7rem;grid-template-columns:34px 1fr;
      margin:0 0 .7rem}.info-strip b,.why-card b{color:#155b9f}
    .info-badge,.why-badge{align-items:center;background:#187fe2;border-radius:50%;color:#fff;
      display:flex;font-weight:850;height:34px;justify-content:center;width:34px}
    .field-note{align-items:center;color:var(--muted-soft);display:flex;font-size:var(--text-small);
      gap:.35rem;line-height:1.4;margin:-.05rem 0 .25rem}
    .field-note .ui-icon{height:15px;width:15px}
    .why-card{align-items:center;display:grid;gap:.7rem;grid-template-columns:34px 1fr;
      margin:0 0 .7rem}.why-card b{display:block;margin-bottom:.1rem}
    .why-badge{font-size:1rem}
    .privacy-line {color:var(--muted);font-size:var(--text-small);text-align:center;margin:.15rem 0;}
    div[data-testid="stButton"] button {border-radius:var(--radius-inner);min-height:42px;
      font-size:var(--text-body);font-weight:750}
    div[data-testid="stButton"] button[kind="primary"] {background:linear-gradient(90deg,#116f72,#16878a);
      border:0;box-shadow:0 7px 18px rgba(20,119,122,.2);min-height:54px;}
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stButton"] button[kind="primary"] p{color:#fff!important}
    div[data-testid="stButton"] button[kind="primary"] p{font-size:1rem!important}
    div[data-testid="stButton"] button[kind="primary"]:disabled{color:#fff!important;opacity:.72}
    div[data-testid="stButton"] button[kind="primary"]:hover {background:#105f62;}

    .coverage-banner{align-items:center;background:linear-gradient(90deg,#e8f7f5,#f4fbfa);
      border:1px solid #cfe6e2;border-radius:var(--radius-inner);color:#50707a;display:flex;
      font-size:var(--text-small);gap:.6rem;margin-top:.5rem;min-height:54px;padding:.42rem .65rem}
    .coverage-icon{align-items:center;background:#d8f0ed;border-radius:50%;color:var(--teal);
      display:flex;flex:0 0 34px;height:34px;justify-content:center;width:34px}
    .coverage-icon .ui-icon{height:19px;width:19px}.coverage-copy{display:block;min-width:0}
    .coverage-banner b{color:#116f72;font-size:var(--text-body);margin-right:.3rem}.coverage-banner a{background:#fff;border:1px solid #bcdad7;
      border-radius:9px;color:var(--teal)!important;font-size:var(--text-small);font-weight:800;
      margin-left:auto;padding:.34rem .55rem;text-decoration:none!important;white-space:nowrap}

    /* Pantalla de análisis */
    .st-key-result_header [data-testid="stHorizontalBlock"]{align-items:center}
    .result-brand{align-items:center;display:flex;gap:.7rem;min-height:50px}
    .result-brand .predi-logo{border-radius:12px;flex-basis:46px;height:46px;width:46px}
    .result-brand-title{color:var(--navy);
      font-size:clamp(1.5rem,1.55vw,1.75rem);font-weight:850;letter-spacing:-.04em;line-height:1.08}
    .result-brand-copy{color:var(--muted);font-size:var(--text-small);margin:.15rem 0 0}
    .result-project-link{align-items:center;background:#fff;border:1px solid #cbdde1;
      border-radius:var(--radius-inner);color:var(--navy)!important;display:flex;
      font-size:var(--text-small);font-weight:800;height:46px;justify-content:center;
      padding:0 .75rem;text-decoration:none!important;white-space:nowrap}
    .result-project-link:hover{background:#f2f8f8;border-color:#9fc8c9;color:var(--teal)!important}
    .st-key-result_header [data-testid="stPopover"]>button,
    .st-key-result_header div[data-testid="stButton"] button{
      border-radius:var(--radius-inner)!important;font-size:var(--text-small)!important;
      font-weight:800!important;height:46px!important;min-height:46px!important;width:100%}
    .st-key-result_header [data-testid="stPopover"]>button{
      background:#fff;border:1px solid #cbdde1;color:var(--navy)}
    .st-key-result_header div[data-testid="stButton"] button[kind="primary"]{
      background:linear-gradient(90deg,#116f72,#16878a);border:1px solid transparent;
      box-shadow:0 6px 16px rgba(20,119,122,.17)}
    .st-key-result_header button p,
    .st-key-result_header div[data-testid="stButton"] button[kind="primary"] p{
      font-size:var(--text-small)!important;white-space:nowrap}
    .result-route-strip{align-items:stretch;background:#fff;border:1px solid var(--line);
      border-radius:var(--radius-inner);display:grid;
      grid-template-columns:1.25fr 1.1fr repeat(4,minmax(0,.9fr));
      margin:.05rem 0 .6rem;overflow:hidden;padding:.55rem .2rem}
    .result-route-item{align-items:center;border-right:1px solid #e1eaec;display:grid;gap:.5rem;
      grid-template-columns:30px 1fr;min-width:0;padding:0 .75rem}.result-route-item:last-child{border-right:0}
    .result-route-item>span:last-child{min-width:0;overflow:hidden}
    .result-route-icon{align-items:center;background:#edf8f7;border-radius:50%;color:var(--teal);
      display:flex;height:30px;justify-content:center;width:30px}.result-route-icon .ui-icon{height:17px;width:17px}
    .result-route-item small{color:var(--muted);display:block;font-size:.66rem;line-height:1.15}
    .result-route-item b{color:var(--navy);display:block;font-size:.82rem;line-height:1.25;
      margin-top:.08rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .result-panel-heading{align-items:center;display:flex;gap:.55rem;margin-bottom:.35rem}
    .result-panel-heading .ui-icon{color:var(--teal);height:22px;width:22px}.result-panel-heading b{
      color:var(--navy);display:block;font-size:var(--text-body);line-height:1.2}
    .result-panel-heading span{color:var(--muted);display:block;font-size:var(--text-small);margin-top:.08rem}
    .result-reading{display:flex;flex-direction:column;gap:.58rem;min-height:454px}
    .result-map-note{align-items:center;
      background:linear-gradient(90deg,#eaf8f7,#f2fbfd);border:1px solid #cfe8e6;
      border-radius:var(--radius-inner);display:grid;gap:.7rem;grid-template-columns:44px 1fr;
      min-height:68px;padding:.62rem .72rem}
    .result-map-note .summary-icon{height:40px;width:40px}.result-map-note b{color:var(--navy);
      display:block;font-size:var(--text-body);line-height:1.3}.result-map-note span{color:var(--muted);
      display:block;font-size:var(--text-small);line-height:1.42;margin-top:.12rem;overflow-wrap:anywhere}
    .result-mini-grid{display:grid;gap:.55rem;grid-template-columns:repeat(2,minmax(0,1fr))}
    .result-mini{align-items:center;background:#fff;border:1px solid var(--line);border-radius:var(--radius-inner);
      display:grid;gap:.5rem;grid-template-columns:34px minmax(0,1fr);min-height:66px;padding:.52rem}
    .result-mini .summary-icon{height:32px;width:32px}.result-mini strong{color:var(--navy);
      display:block;font-size:.9rem;line-height:1.1}.result-mini small{color:var(--muted);display:block;
      font-size:var(--text-small);line-height:1.32;margin-top:.12rem;overflow-wrap:anywhere}.result-mini.high .summary-icon{background:#ffedef;color:#d93e54}
    .result-guide{background:linear-gradient(100deg,#f8fbfb,#eef7ff);border:1px solid #d9e8ea;
      border-radius:var(--radius-inner);display:flex;flex:1;flex-direction:column;padding:.7rem .75rem}
    .result-guide-head{align-items:center;display:flex;gap:.6rem;justify-content:space-between;
      margin-bottom:.58rem}.result-guide-head b{color:var(--navy);font-size:.78rem}
    .result-guide-head a{background:#fff;border:1px solid #97ced0;border-radius:8px;
      color:var(--teal)!important;font-size:.66rem;font-weight:800;padding:.32rem .55rem;
      text-decoration:none!important;white-space:nowrap}
    .result-guide-grid{display:grid;gap:.6rem;grid-template-columns:1fr 1fr}.result-guide-item{
      color:var(--muted);display:grid;font-size:var(--text-small);gap:.48rem;
      grid-template-columns:28px minmax(0,1fr);line-height:1.42}.result-guide-item i{
      align-items:center;background:#e3f4f3;border-radius:50%;color:var(--teal);display:flex;
      font-style:normal;font-weight:850;height:28px;justify-content:center;width:28px}
    .result-guide-item.warning i{background:#ffedef;color:#d93e54}.result-guide-item b{
      color:var(--navy);display:block;font-size:.74rem;margin-bottom:.1rem}
    .result-guide-foot{border-top:1px solid #dce9ec;color:var(--muted);font-size:var(--text-small);
      line-height:1.4;margin-top:auto;padding-top:.55rem}
    .highlight-shell,.detail-shell{background:#fff;border:1px solid var(--line);border-radius:var(--radius);
      box-shadow:var(--shadow);padding:.65rem .8rem}.highlight-shell{margin-bottom:.75rem}.highlight-grid{align-items:stretch;display:grid;gap:.7rem;
      grid-template-columns:repeat(3,minmax(0,1fr))}.highlight-grid.count-1{grid-template-columns:1fr}
    .highlight-grid.count-2{grid-template-columns:repeat(2,minmax(0,1fr))}
    .highlight-card{--card-color:#2e8b57;align-items:flex-start;
      background:#fff;border:1px solid var(--line);border-left:5px solid var(--card-color);
      border-radius:var(--radius-inner);display:grid;gap:.65rem;grid-template-columns:36px minmax(0,1fr);
      height:100%;min-height:86px;overflow:hidden;padding:.65rem}.highlight-pin{align-items:center;background:#edf7f7;
      border-radius:50%;color:var(--teal);display:flex;height:36px;justify-content:center;width:36px}
    .highlight-pin .ui-icon{height:18px;width:18px}.highlight-content{min-width:0;width:100%}
    .highlight-top{align-items:flex-start;display:flex;gap:.6rem;justify-content:space-between}
    .highlight-route{color:var(--navy);font-size:.77rem;font-weight:800;line-height:1.3;
      min-width:0;overflow-wrap:anywhere}.highlight-meta{color:var(--muted);font-size:.66rem;font-weight:600;
      line-height:1.4;margin-top:.22rem}.highlight-pill,.detail-pill{background:var(--card-color);
      border-radius:999px;color:#fff;font-size:.66rem;font-weight:800;padding:.3rem .55rem;white-space:nowrap}
    .highlight-state{border-top:1px solid #f1dadd;color:#9d413a;font-size:.62rem;
      line-height:1.35;margin-top:.4rem;padding-top:.35rem}
    .highlight-empty{background:#f7fafb;border:1px dashed #ccdadd;border-radius:var(--radius-inner);
      color:var(--muted);font-size:var(--text-small);padding:.8rem;text-align:center}
    .detail-shell{clear:both;isolation:isolate;margin:.35rem 0 .8rem;padding-bottom:.7rem;position:relative}
    .detail-heading-count{color:var(--navy);font-size:var(--text-small);
      font-weight:800;margin-left:auto}.detail-table{border:1px solid var(--line);border-radius:var(--radius-inner);
      max-width:100%;overflow-x:auto;overflow-y:hidden;position:relative;width:100%}
    .detail-head,.detail-row{align-items:start;display:grid;gap:.75rem;
      grid-template-columns:minmax(38px,.28fr) minmax(105px,.72fr) minmax(260px,1.75fr)
      minmax(170px,.95fr) minmax(180px,1.3fr) minmax(130px,.72fr);
      line-height:1.38;min-width:1040px;padding:.58rem .7rem}
    .detail-head>*,.detail-row>*{box-sizing:border-box;min-width:0;overflow-wrap:anywhere}
    .detail-head{align-items:center;background:#f0f6f7;color:#496473;font-size:.7rem;font-weight:800}
    .detail-row{border-top:1px solid #e6edef;color:#496473;font-size:var(--text-small);min-height:52px}
    .detail-row:nth-child(odd){background:#f8fbfc}.detail-row b{color:var(--navy)}
    .detail-row small{color:#9b554f;display:block;font-size:.67rem;line-height:1.35;margin-top:.25rem}
    .detail-pill{--card-color:#6f8794;background:#e7eef2;color:#516977;display:inline-block;text-align:center}
    .detail-pill.high{background:#ffe5e8;color:#df304a}.detail-pill.medium{background:#fff0d6;color:#db8a22}

    /* Metodología resumida al final del resultado */
    .st-key-result_method{margin:.15rem 0 .8rem}
    .st-key-result_method [data-testid="stExpander"]{background:#fff;border:1px solid var(--line)!important;
      border-radius:var(--radius)!important;box-shadow:var(--shadow);overflow:hidden}
    .st-key-result_method [data-testid="stExpander"] details>summary{background:#fbfdfd;
      min-height:52px;padding:.15rem .9rem}
    .st-key-result_method [data-testid="stExpander"] details>summary:hover{background:#f3f9f8}
    .st-key-result_method [data-testid="stExpander"] details>summary p{color:var(--navy)!important;
      font-size:var(--text-heading)!important;font-weight:800!important;letter-spacing:-.015em}
    .st-key-result_method [data-testid="stExpanderDetails"]{border-top:1px solid #e6edef;
      padding:.8rem .9rem .9rem!important}
    .method-intro{color:var(--muted);font-size:var(--text-body);line-height:1.5;
      margin:0 0 .75rem}
    .method-grid{align-items:stretch;display:grid;gap:.7rem;
      grid-template-columns:repeat(4,minmax(0,1fr))}
    .method-card{background:linear-gradient(180deg,#fff,#fbfdfd);border:1px solid var(--line);
      border-radius:var(--radius-inner);display:grid;gap:.7rem;grid-template-columns:48px minmax(0,1fr);
      min-height:150px;padding:.8rem}
    .method-card-icon{align-items:center;background:#e6f3f2;border-radius:50%;color:var(--teal);
      display:flex;height:48px;justify-content:center;width:48px}
    .method-card-icon .ui-icon{height:25px;width:25px}.method-card-copy{min-width:0}
    .method-card b{color:var(--navy);display:block;font-size:var(--text-body);line-height:1.25;
      margin:.08rem 0 .3rem}.method-card span{color:var(--muted);display:block;
      font-size:var(--text-small);line-height:1.48}
    .method-cta{align-items:center;background:#fff;border:1px solid #79bec0;border-radius:var(--radius-inner);
      color:var(--teal)!important;display:flex;font-size:var(--text-body);font-weight:800;
      justify-content:center;margin-top:.75rem;min-height:44px;padding:.3rem .8rem;
      text-decoration:none!important;transition:.15s ease}
    .method-cta:hover{background:#edf8f7;border-color:var(--teal-dark);color:var(--teal-dark)!important}

    @media(max-width:960px){
      .block-container{padding:.45rem .75rem 2rem}.hero-art{height:115px;opacity:.26;width:100%}
      .predi-brand{align-items:flex-start;gap:.65rem}.predi-logo{border-radius:12px;flex-basis:44px;
        height:44px;width:44px}.predi-title{font-size:1.75rem;line-height:1.08}
      .predi-subtitle{font-size:var(--text-body);margin:.55rem 0 .75rem}
      .method-link{margin:0 0 .65rem;min-height:42px}.hero-motto{display:none}
      .feature-ribbon{gap:.4rem;margin-bottom:.7rem}.feature-chip{display:flex;gap:.4rem;
        min-height:48px;padding:.45rem}.feature-icon{flex:0 0 30px;height:30px;width:30px}
      .feature-icon .ui-icon{height:16px;width:16px}.feature-chip b{font-size:0}
      .feature-chip b::after{content:attr(data-mobile);font-size:var(--text-small)}
      .feature-chip>div:last-child>span{display:none}.panel-title{margin-bottom:.45rem}.panel-icon{flex-basis:40px;
        height:40px;width:40px}.panel-title strong{font-size:var(--text-heading)}
      .panel-title span{font-size:var(--text-small)}div[data-testid="stVerticalBlockBorderWrapper"]{
        border-radius:14px}.panel-tag{display:none}.coverage-banner{align-items:center;
        line-height:1.35;margin-top:.4rem;min-height:64px;padding:.55rem}.coverage-banner a{display:none}
      .coverage-copy{display:flex;flex-direction:column}.coverage-icon{flex-basis:34px;height:34px;width:34px}
      .result-brand-title{font-size:1.45rem}.result-route-strip{
        grid-template-columns:repeat(2,1fr)}.result-route-item{border-bottom:1px solid #e1eaec;
        min-height:48px}.result-route-item:nth-child(2n){border-right:0}.result-reading{min-height:0}
      .result-guide-grid,.highlight-grid{grid-template-columns:1fr}.detail-head,.detail-row{min-width:1040px}
      .highlight-card{min-height:auto}
      .highlight-top{flex-wrap:wrap}
      .method-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.method-card{min-height:132px}
    }
    @media(max-width:560px){
      .block-container{padding:.4rem .55rem 1.5rem}.predi-title{font-size:1.58rem}
      .feature-ribbon{grid-template-columns:repeat(3,minmax(0,1fr))}.feature-chip{justify-content:center}
      .feature-chip>div:last-child{min-width:0}.feature-chip b{overflow:hidden;text-overflow:ellipsis;
        white-space:nowrap}.panel-title span{line-height:1.3}
      .method-grid{grid-template-columns:1fr}.method-card{grid-template-columns:38px minmax(0,1fr);
        min-height:auto;padding:.65rem}.method-card-icon{height:38px;width:38px}
      .method-card-icon .ui-icon{height:20px;width:20px}.method-intro{font-size:var(--text-small)}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def icono(nombre: str) -> str:
    """Devuelve un icono lineal consistente con la identidad visual."""

    trazos = {
        "ruta": '<path d="M4 7.5h4l3 4h4l3 4h2"/><path d="M4 16.5h4l3-4"/>',
        "ubicacion": '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
        "tramos": '<path d="M5 19V10M10 19V5M15 19v-7M20 19V8"/>',
        "clima": '<path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 11.5 3.5 3.5 0 0 0 7 18Z"/><path d="M8 4 7 2M16 4l1-2M19 7h2"/>',
        "mapa": '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3Z"/><path d="M9 3v15M15 6v15"/>',
        "persona": '<circle cx="12" cy="8" r="3"/><path d="M5 21a7 7 0 0 1 14 0"/>',
        "escudo": '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-5"/>',
        "lluvia": '<path d="M7 16h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 9.5 3.5 3.5 0 0 0 7 16Z"/><path d="m9 19-1 2M13 19l-1 2M17 19l-1 2"/>',
        "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "distancia": '<path d="M5 18c0-4 4-4 4-8s4-4 4-1 3 3 6 1"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="10" r="2"/>',
        "documento": '<path d="M6 2h8l4 4v16H6Z"/><path d="M14 2v5h5M9 12h6M9 16h6"/>',
        "google": (
            '<path d="M12 22s7-6.2 7-13A7 7 0 0 0 5 9c0 6.8 7 13 7 13Z" '
            'fill="#4285F4" stroke="none"/><path d="M12 2a7 7 0 0 1 5.8 3.1L13.9 9A2 2 0 0 0 12 7Z" '
            'fill="#EA4335" stroke="none"/><path d="M5.7 5.9 10 10.2A2 2 0 0 0 12 11v11S5 15.8 5 9a7 7 0 0 1 .7-3.1Z" '
            'fill="#34A853" stroke="none"/><path d="M17.8 5.1 13.9 9A2 2 0 0 1 12 11l4.1 4.1C17.8 13 19 10.8 19 9a7 7 0 0 0-1.2-3.9Z" '
            'fill="#FBBC04" stroke="none"/><circle cx="12" cy="9" r="2" fill="#fff" stroke="none"/>'
        ),
        "barras": '<rect x="4" y="13" width="4" height="7" rx="1" fill="currentColor" stroke="none"/><rect x="10" y="8" width="4" height="12" rx="1" fill="currentColor" stroke="none"/><rect x="16" y="4" width="4" height="16" rx="1" fill="currentColor" stroke="none"/>',
        "clima_color": (
            '<circle cx="15.5" cy="8" r="4" fill="#FDB813" stroke="none"/>'
            '<path d="M15.5 1.5V3M15.5 13v1.5M9 8H7.5M23.5 8H22M11 3.5 10 2.4M21 13.6l-1-1.1M20 3.5l1-1.1" stroke="#F59E0B"/>'
            '<path d="M6.5 19h10a3.5 3.5 0 0 0 .5-7A5.4 5.4 0 0 0 6.5 13 3 3 0 0 0 6.5 19Z" fill="#35B8E8" stroke="#1686B2"/>'
        ),
    }
    contenido = trazos.get(nombre, trazos["ruta"])
    return f'<svg class="ui-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">{contenido}</svg>'


def arte_cabecera() -> str:
    """Ilustración vectorial ligera inspirada en el perfil urbano de Bogotá."""

    return """
    <div class="hero-art" aria-hidden="true"><svg viewBox="0 0 1200 180" preserveAspectRatio="none">
      <path d="M0 145 120 92l98 39 125-82 118 69 142-91 116 85 104-59 130 79 137-54 130 52v50H0Z" fill="#e8f6fc"/>
      <path d="M0 160 142 125l102 25 133-62 116 55 128-72 126 70 99-43 136 57 118-37 120 30v42H0Z" fill="#dff1f8" opacity=".8"/>
      <g fill="#74bedb" opacity=".47">
        <rect x="535" y="102" width="16" height="58"/><rect x="558" y="84" width="21" height="76"/>
        <rect x="586" y="112" width="17" height="48"/><rect x="612" y="67" width="24" height="93"/>
        <rect x="642" y="93" width="15" height="67"/><rect x="665" y="41" width="28" height="119"/>
        <path d="M671 41h16l-4-18h-8Z"/><rect x="704" y="105" width="20" height="55"/>
        <rect x="734" y="76" width="26" height="84"/><rect x="770" y="95" width="17" height="65"/>
        <rect x="797" y="60" width="23" height="100"/><rect x="831" y="107" width="18" height="53"/>
        <rect x="859" y="87" width="29" height="73"/><rect x="897" y="116" width="19" height="44"/>
        <rect x="929" y="72" width="24" height="88"/><rect x="965" y="98" width="18" height="62"/>
      </g>
      <g fill="#b7e1d7" opacity=".75"><circle cx="1020" cy="148" r="25"/><circle cx="1070" cy="142" r="32"/><circle cx="1125" cy="148" r="28"/><circle cx="1172" cy="139" r="36"/></g>
    </svg></div>
    """


def encabezado(titulo: str, subtitulo: str, con_arte: bool = False) -> None:
    arte = arte_cabecera() if con_arte else ""
    st.markdown(
        f"""
        {arte}<div class="predi-brand"><div class="predi-logo">{icono_marca()}</div>
        <div class="predi-title">{html.escape(titulo)}</div></div>
        <p class="predi-subtitle">{html.escape(subtitulo)}</p>
        """,
        unsafe_allow_html=True,
    )


def validar_formulario(
    origen: dict | None,
    destino: dict | None,
    salida: datetime,
    consentimiento: bool,
) -> list[str]:
    ahora = datetime.now(ZONA_BOGOTA)
    errores = []
    if not origen:
        errores.append("selecciona el origen desde las sugerencias")
    if not destino:
        errores.append("selecciona el destino desde las sugerencias")
    if origen and destino and origen.get("place_id") == destino.get("place_id"):
        errores.append("el origen y el destino deben ser diferentes")
    if salida < ahora.replace(second=0, microsecond=0):
        errores.append("elige una salida que no esté en el pasado")
    if not consentimiento:
        errores.append("confirma el uso temporal de los datos")
    if not PLACES_API_KEY:
        errores.append("configura la clave de Google Places")
    if not MAPS_BROWSER_KEY:
        errores.append("configura la clave de Google Maps del navegador")
    return errores


def solicitar_prediccion(payload: dict) -> dict | None:
    try:
        respuesta = requests.post(API_URL, json=payload, timeout=120)
    except requests.Timeout:
        st.error("El análisis tardó más de lo esperado. Intenta nuevamente.")
        return None
    except requests.RequestException:
        st.error("No pudimos conectar con PrediRuta. Comprueba que la API esté activa.")
        return None

    try:
        contenido = respuesta.json()
    except ValueError:
        contenido = {}
    if respuesta.ok:
        tramos = contenido.get("tramos", [])
        if tramos and any(
            not (tramo.get("ubicacion_tramo") or {}).get("desde")
            or not (tramo.get("ubicacion_tramo") or {}).get("hasta")
            for tramo in tramos
        ):
            st.error(
                "La API conectada no entregó la ubicación completa de todos los "
                "tramos. Actualiza también el servicio backend antes de continuar."
            )
            with st.expander("Información para soporte"):
                st.code(f"Backend: {API_URL}\nContrato esperado: ubicacion_tramo")
            return None
        return contenido

    detalle = str(contenido.get("detail", "No fue posible completar la consulta."))
    if "are blocked" in detalle or "API_KEY_SERVICE_BLOCKED" in detalle:
        st.error(
            "La configuración de Google Maps del backend aún no está disponible. "
            "La pantalla podría estar conectada a una instancia anterior."
        )
        with st.expander("Información para soporte"):
            st.code(f"Backend: {API_URL}\n{detalle}")
    elif respuesta.status_code == 422 and "sale del área urbana" in detalle:
        st.error(
            "No podemos analizar este trayecto porque la ruta propuesta por Google "
            "sale de Bogotá. Prueba cambiar el origen, el destino o la hora de salida."
        )
    elif respuesta.status_code == 422:
        st.warning(detalle)
    elif respuesta.status_code == 502:
        if "GOOGLE_APIKEY" in detalle:
            st.error(
                "PrediRuta no tiene disponible la credencial necesaria para consultar "
                "la ruta y el clima. Revisa la configuración del servicio de la API."
            )
        elif "Weather" in detalle or "pronóstico" in detalle:
            st.error(
                "Pudimos procesar la ruta, pero el pronóstico no respondió con toda "
                "la información necesaria. Intenta nuevamente en unos minutos."
            )
        elif "Routes" in detalle or "recorrido" in detalle:
            st.error(
                "Google Maps no pudo calcular este recorrido. Revisa los puntos "
                "seleccionados o intenta con otra hora de salida."
            )
        else:
            st.error(
                "Uno de los servicios de Google no respondió correctamente. "
                "Puedes intentar nuevamente en unos minutos."
            )
        with st.expander("Detalle para soporte"):
            st.code(f"Backend: {API_URL}\n{detalle}")
    else:
        st.error(detalle)
    return None


def nueva_consulta() -> None:
    st.session_state.resultado = None
    st.session_state.consulta = None
    for clave in (
        "lugar_origen", "lugar_destino", "fecha_comparacion", "hora_comparacion",
        "hora_salida",
    ):
        st.session_state.pop(clave, None)


def mostrar_planeacion() -> None:
    columna_encabezado, columna_metodologia = st.columns([4.5, 1.25])
    with columna_encabezado:
        encabezado(
            "PrediRuta | Analiza la criticidad de cada tramo de tu recorrido",
            "PrediRuta analiza los tramos de una ruta en Bogotá y estima su criticidad a partir de patrones históricos de accidentalidad, el contexto del recorrido y el clima previsto. La ruta, los tiempos y el clima son proporcionados por Google.",
            con_arte=True,
        )
    with columna_metodologia:
        st.markdown(
            '<a class="method-link" href="?vista=proyecto" target="_self" '
            'title="Metodología, modelos, resultados y limitaciones">'
            'Conoce el proyecto →</a><div class="hero-motto">Rutas más seguras comprendiendo<br>'
            "el contexto de tu recorrido</div>",
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
        <div class="feature-ribbon">
          <div class="feature-chip"><div class="feature-icon">{icono("google")}</div><div><b data-mobile="Ruta">Ruta de Google Maps</b>
          <span>Usamos la ruta más probable generada por Google Maps.</span></div></div>
          <div class="feature-chip"><div class="feature-icon">{icono("barras")}</div><div><b data-mobile="Tramos">Análisis por tramos</b>
          <span>Evaluamos la criticidad de cada segmento con patrones históricos de siniestros.</span></div></div>
          <div class="feature-chip"><div class="feature-icon">{icono("clima_color")}</div><div><b data-mobile="Clima">Clima y contexto</b>
          <span>La fecha, hora y otras condiciones ayudan a interpretar mejor el escenario.</span></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ahora = datetime.now(ZONA_BOGOTA).replace(second=0, microsecond=0)
    salida_inicial = ahora
    # Una clave explícita evita que el valor se regenere con la hora actual en
    # cada rerun. El usuario puede escribir cualquier minuto y conservarlo.
    st.session_state.setdefault("hora_salida", salida_inicial.time())
    fecha_maxima = ahora.date() + timedelta(days=DIAS_PRONOSTICO - 1)
    columna_formulario, columna_mapa = st.columns([0.95, 1.18], gap="small")

    with columna_formulario:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="panel-title"><div class="panel-icon">{icono("ubicacion")}</div><div>
                <strong>Consulta la criticidad de una ruta</strong>
                <span>Selecciona origen, destino, fecha y hora. Esta información define el recorrido que analizaremos.</span>
                </div></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="info-strip"><span class="info-badge">i</span><span>'
                '<b>La ruta es proporcionada por Google Maps.</b> PrediRuta no genera '
                'ni modifica el recorrido seleccionado.</span></div>',
                unsafe_allow_html=True,
            )
            columna_origen, columna_destino = st.columns(2)
            with columna_origen:
                origen = seleccionar_lugar(
                    PLACES_API_KEY, "Punto de origen", "Ej. Portal Norte",
                    "origin", "lugar_origen",
                )
            with columna_destino:
                destino = seleccionar_lugar(
                    PLACES_API_KEY, "Punto de destino", "Ej. Universidad de los Andes",
                    "destination", "lugar_destino",
                )
            columna_fecha, columna_hora = st.columns(2)
            with columna_fecha:
                fecha_salida = st.date_input(
                    "Fecha del viaje", value=salida_inicial.date(), min_value=ahora.date(),
                    max_value=fecha_maxima,
                    help="Puedes consultar hoy y los próximos seis días.",
                )
            with columna_hora:
                hora_salida = st.time_input(
                    "Hora de salida", step=60, key="hora_salida",
                    help="Google usa esta hora para calcular un escenario alto de tráfico.",
                )
            st.markdown(
                f'<div class="field-note">{icono("reloj")}<span>La fecha y la hora permiten definir el contexto temporal del recorrido y consultar el pronóstico meteorológico.</span></div>',
                unsafe_allow_html=True,
            )

        with st.container(border=True):
            st.markdown(
                f"""
                <div class="panel-title"><div class="panel-icon">{icono("persona")}</div><div>
                <strong>Información complementaria</strong>
                <span>Estos datos ayudan a contextualizar el escenario del viaje cuando existen patrones históricos comparables.</span>
                </div></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="why-card"><span class="why-badge">?</span><span>'
                '<b>¿Por qué pedimos estos datos?</b> Contextualizan el posible estado del actor '
                'únicamente en los tramos prioritarios. No cambian la ruta ni reemplazan el '
                'análisis principal por tramo.</span></div>',
                unsafe_allow_html=True,
            )
            columna_edad, columna_genero = st.columns(2)
            with columna_edad:
                edad = st.number_input("Edad", min_value=0, max_value=110, value=35)
            with columna_genero:
                genero_texto = st.selectbox("Género", list(GENEROS), index=0)
            columna_vehiculo, columna_servicio = st.columns(2)
            with columna_vehiculo:
                clase_texto = st.selectbox("Vehículo", list(CLASES_VEHICULO), index=0)
            with columna_servicio:
                servicio_texto = st.selectbox(
                    "Servicio del vehículo", list(SERVICIOS_VEHICULO), index=3
                )
            consentimiento = st.checkbox(
                "Entiendo que mis datos se usan solo para este análisis de PrediRuta, "
                "no se almacenan ni se utilizan para otro fin."
            )
            salida = datetime.combine(fecha_salida, hora_salida, tzinfo=ZONA_BOGOTA)
            errores = validar_formulario(origen, destino, salida, consentimiento)
            if errores:
                st.caption("Para continuar: " + "; ".join(errores) + ".")
            analizar = st.button(
                "Analizar mi trayecto  →", type="primary", width="stretch",
                disabled=bool(errores),
            )
            st.markdown(
                '<div class="privacy-line">▣ &nbsp;PrediRuta analiza la ruta sugerida por '
                'Google Maps; no genera la ruta.</div>',
                unsafe_allow_html=True,
            )

    with columna_mapa:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="panel-tag">Bogotá, Colombia</div>
                <div class="panel-title map-title"><div class="panel-icon">{icono("mapa")}</div><div>
                <strong>Vista previa de la ruta</strong>
                <span>Confirma visualmente el recorrido antes de ejecutar el análisis.</span>
                </div></div>
                """,
                unsafe_allow_html=True,
            )
            mostrar_mapa_previo(
                MAPS_BROWSER_KEY, origen, destino, salida.isoformat(),
                "mapa_planeacion", height=610,
            )
        st.markdown(
            f"""
            <div class="coverage-banner"><span class="coverage-icon">{icono("escudo")}</span>
            <span class="coverage-copy"><b>Cobertura actual: Bogotá urbana</b>
            <span>Disponible únicamente en las zonas urbanas cubiertas por el entrenamiento del modelo.</span></span>
            <a href="?vista=proyecto" target="_self">Conoce más →</a></div>
            """,
            unsafe_allow_html=True,
        )

    if analizar:
        payload = {
            "origen": origen["address"],
            "destino": destino["address"],
            "origen_coordenadas": {
                "latitud": origen["lat"], "longitud": origen["lng"]
            },
            "destino_coordenadas": {
                "latitud": destino["lat"], "longitud": destino["lng"]
            },
            "fecha_salida": fecha_salida.isoformat(),
            "hora_salida": hora_salida.strftime("%H:%M"),
            "perfil_actor": {
                "edad": int(edad), "genero": GENEROS[genero_texto],
                "clase_vehiculo": CLASES_VEHICULO[clase_texto],
                "servicio_vehiculo": SERVICIOS_VEHICULO[servicio_texto],
            },
            "consentimiento_datos": consentimiento,
        }
        with st.spinner("Analizando la ruta, el tráfico y el clima de cada tramo…"):
            resultado = solicitar_prediccion(payload)
        if resultado:
            st.session_state.resultado = resultado
            st.session_state.consulta = {
                "origen": origen["name"] or origen["address"],
                "destino": destino["name"] or destino["address"],
                "salida": salida.isoformat(),
                # Se conserva en sesión para comparar horarios sin volver a
                # pedir ubicaciones ni información complementaria.
                "payload": payload,
            }
            st.rerun()


def hora_paso_legible(tramo: dict) -> str:
    """Evita rangos engañosos como ``10:00 - 10:00`` en tramos muy cortos."""

    hora_paso = str(tramo.get("hora_paso", ""))
    inicio, separador, fin = hora_paso.partition(" - ")
    if separador and inicio == fin:
        return f"{inicio} aprox."
    return hora_paso


def _distancia_legible(tramo: dict) -> str:
    distancia = float(tramo.get("distancia_metros", 0))
    return f"{distancia / 1000:.1f} km" if distancia >= 1000 else f"{distancia:.0f} m"


def _etiqueta_coincidencia(tramo: dict) -> tuple[str, str]:
    nivel = tramo.get("nivel_criticidad", "Bajo")
    if nivel == "Alto":
        return "Similitud histórica alta", "high"
    if nivel == "Medio":
        return "Similitud histórica media", "medium"
    return "Similitud histórica baja", "low"


def _nombre_tramo(tramo: dict) -> str:
    # ``ubicacion_sector`` permite visualizar resultados creados por una
    # versión anterior durante la misma sesión; la API nueva usa "tramo".
    ubicacion = (
        tramo.get("ubicacion_tramo")
        or tramo.get("ubicacion_sector")
        or {}
    )
    desde, hasta = ubicacion.get("desde"), ubicacion.get("hasta")
    if desde and hasta:
        return f"{desde} → {hasta}"
    puntos = tramo.get("puntos_polyline") or []
    if puntos:
        inicio, fin = puntos[0], puntos[-1]
        return (
            f"{float(inicio[0]):.5f}, {float(inicio[1]):.5f} → "
            f"{float(fin[0]):.5f}, {float(fin[1]):.5f}"
        )
    return "Ubicación del tramo no disponible"


def _tarjeta_destacada(tramo: dict) -> str:
    etiqueta, _ = _etiqueta_coincidencia(tramo)
    clima = tramo["clima"]
    estado_html = ""
    if tramo.get("estado_actor"):
        estado = tramo["estado_actor"]
        probable = estado["estado_mas_probable"].capitalize()
        porcentaje = estado["probabilidades"][estado["estado_mas_probable"]]
        estado_html = (
            '<div class="highlight-state">Estado más compatible si ocurre un siniestro: '
            f"{html.escape(probable)} ({porcentaje:.0%}).</div>"
        )
    return (
        f'<div class="highlight-card" style="--card-color:{tramo["color"]}">'
        f'<div class="highlight-pin">{icono("ubicacion")}</div><div class="highlight-content">'
        '<div class="highlight-top">'
        f'<div class="highlight-route">{html.escape(_nombre_tramo(tramo))}</div>'
        f'<span class="highlight-pill">{html.escape(etiqueta)}</span></div>'
        f'<div class="highlight-meta">{html.escape(hora_paso_legible(tramo))} · '
        f'{html.escape(tramo["duracion"])} · {_distancia_legible(tramo)} · '
        f'{clima["probabilidad_precipitacion"]:.0f}% lluvia</div>'
        f'{estado_html}</div></div>'
    )


def _fila_detalle(tramo: dict) -> str:
    etiqueta, clase = _etiqueta_coincidencia(tramo)
    clima = tramo["clima"]
    estado = tramo.get("estado_actor")
    estado_html = ""
    if estado:
        probable = estado["estado_mas_probable"].capitalize()
        estado_html = f'<small>Si ocurriera siniestro: {html.escape(probable)}</small>'
    return (
        '<div class="detail-row">'
        f'<b>{tramo["tramo"]}</b><b>{html.escape(hora_paso_legible(tramo))}</b>'
        f'<span>{html.escape(_nombre_tramo(tramo))}</span>'
        f'<span><span class="detail-pill {clase}">{html.escape(etiqueta)}</span>{estado_html}</span>'
        f'<span>{html.escape(clima["condicion"])} · {clima["temperatura"]:.1f} °C · '
        f'{clima["probabilidad_precipitacion"]:.0f}% lluvia</span>'
        f'<span><b>{html.escape(tramo["duracion"])}</b> · {_distancia_legible(tramo)}</span></div>'
    )


def _comparar_otro_horario(consulta: dict, salida_actual: datetime) -> None:
    """Repite el análisis cambiando solo la fecha y hora del mismo trayecto."""

    payload_base = consulta.get("payload")
    with st.popover(
        "Analizar otro horario", icon=":material/sync:",
        disabled=not bool(payload_base), width="stretch",
    ):
        st.markdown("**Mismo trayecto, otra hora**")
        st.caption("Conservamos los puntos y la información complementaria.")
        ahora = datetime.now(ZONA_BOGOTA).replace(second=0, microsecond=0)
        fecha = st.date_input(
            "Nueva fecha", value=max(salida_actual.date(), ahora.date()),
            min_value=ahora.date(),
            max_value=ahora.date() + timedelta(days=DIAS_PRONOSTICO - 1),
            key="fecha_comparacion",
        )
        hora = st.time_input(
            "Nueva hora de salida", value=salida_actual.time(), step=60,
            key="hora_comparacion",
        )
        nueva_salida = datetime.combine(fecha, hora, tzinfo=ZONA_BOGOTA)
        invalida = nueva_salida < ahora
        if invalida:
            st.caption("Elige una salida que no esté en el pasado.")
        if st.button(
            "Actualizar comparación", type="primary", width="stretch",
            disabled=invalida, key="actualizar_horario",
        ):
            payload = {
                **payload_base,
                "fecha_salida": fecha.isoformat(),
                "hora_salida": hora.strftime("%H:%M"),
            }
            with st.spinner("Comparando el nuevo horario…"):
                resultado = solicitar_prediccion(payload)
            if resultado:
                st.session_state.resultado = resultado
                st.session_state.consulta = {
                    **consulta, "salida": nueva_salida.isoformat(), "payload": payload
                }
                st.rerun()


def mostrar_resultado() -> None:
    data = st.session_state.resultado
    consulta = st.session_state.consulta or {}
    resumen = data["resumen"]
    tramos = data["tramos"]
    salida_iso = consulta.get("salida") or tramos[0].get("hora_inicio")
    salida = datetime.fromisoformat(salida_iso)

    with st.container(key="result_header"):
        columna_titulo, columna_proyecto, columna_comparar, columna_nueva = st.columns(
            [5.1, 1.3, 1.3, 1.3], gap="small"
        )
        with columna_titulo:
            st.markdown(
                f'<div class="result-brand"><div class="predi-logo">{icono_marca()}</div><div>'
                '<div class="result-brand-title">PrediRuta | Análisis de tu trayecto</div>'
                '<div class="result-brand-copy">Compara tu recorrido con patrones históricos y '
                'condiciones previstas de paso.</div></div></div>',
                unsafe_allow_html=True,
            )
        with columna_proyecto:
            st.markdown(
                '<a class="result-project-link" href="?vista=proyecto" target="_self">'
                'ⓘ &nbsp; Conoce el proyecto</a>', unsafe_allow_html=True,
            )
        with columna_comparar:
            _comparar_otro_horario(consulta, salida)
        with columna_nueva:
            st.button(
                "Nueva consulta", icon=":material/add:", type="primary",
                on_click=nueva_consulta, width="stretch",
            )

    items_resumen = (
        ("ubicacion", "Desde", consulta.get("origen", "Origen")),
        ("mapa", "Hasta", consulta.get("destino", "Destino")),
        ("reloj", "Salida", f"{salida:%d/%m · %H:%M}"),
        ("reloj", "Tiempo conservador", resumen["duracion_estimada"]),
        ("distancia", "Distancia total", f'{resumen["distancia_total_km"]:.1f} km'),
        ("tramos", "Tramos analizados", str(resumen["total_tramos"])),
    )
    st.markdown(
        '<div class="result-route-strip">'
        + "".join(
            f'<div class="result-route-item"><span class="result-route-icon">{icono(tipo)}</span>'
            f'<span><small>{html.escape(etiqueta)}</small><b>{html.escape(str(valor))}</b></span></div>'
            for tipo, etiqueta, valor in items_resumen
        )
        + "</div>", unsafe_allow_html=True,
    )

    altos = [tramo for tramo in tramos if tramo["nivel_criticidad"] == "Alto"]
    lluvias = [float(tramo["clima"]["probabilidad_precipitacion"]) for tramo in tramos]
    lluvia_texto = (
        f"{min(lluvias):.0f}% – {max(lluvias):.0f}%"
        if min(lluvias) != max(lluvias) else f"{max(lluvias):.0f}%"
    )

    columna_mapa, columna_lectura = st.columns([1.75, .75], gap="small")
    with columna_mapa:
        with st.container(border=True):
            st.markdown(
                f'<div class="result-panel-heading">{icono("mapa")}<div><b>Mapa del recorrido</b>'
                '<span>La ruta la define Google Maps; PrediRuta analiza sus tramos.</span></div></div>',
                unsafe_allow_html=True,
            )
            mostrar_mapa_resultado(MAPS_BROWSER_KEY, data, "mapa_resultado", height=440)
    with columna_lectura:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="result-reading">
                  <div class="result-panel-heading">{icono("barras")}<div><b>Lectura del resultado</b></div></div>
                  <div class="result-map-note"><div class="summary-icon">{icono("ubicacion")}</div><div>
                    <b>Explora cada tramo en el mapa</b><span>Haz clic sobre una línea del recorrido para consultar su hora de paso, clima y criticidad estimada.</span></div></div>
                  <div class="result-mini-grid">
                    <div class="result-mini high"><div class="summary-icon">!</div><div><strong>{len(altos)}</strong><small>tramos con coincidencia alta</small></div></div>
                    <div class="result-mini"><div class="summary-icon">{icono("lluvia")}</div><div><small>Lluvia prevista</small><strong>{lluvia_texto}</strong></div></div>
                  </div>
                  <div class="result-guide"><div class="result-guide-head"><b>Cómo interpretar la lectura</b>
                    <a href="?vista=proyecto" target="_self">Conoce el proyecto &nbsp;→</a></div>
                    <div class="result-guide-grid">
                      <div class="result-guide-item"><i>i</i><div><b>Qué significa</b><span>Algunos tramos se parecen más a escenarios históricos observados por el modelo.</span></div></div>
                      <div class="result-guide-item warning"><i>!</i><div><b>Qué no significa</b><span>No representa una probabilidad individual de accidente ni una recomendación automática.</span></div></div>
                    </div>
                    <div class="result-guide-foot">Los tramos destacados aparecen debajo; la tabla conserva el detalle completo del recorrido.</div>
                  </div>
                </div>
                """, unsafe_allow_html=True,
            )

    destacados = sorted(
        altos, key=lambda tramo: tramo.get("prioridad_recorrido") or 999
    )
    st.markdown(
        f'<div class="highlight-shell"><div class="result-panel-heading">{icono("ubicacion")}<div>'
        '<b>Tramos destacados</b><span>Tramos con mayor criticidad estimada dentro del recorrido.</span>'
        f'</div></div><div class="highlight-grid count-{max(1, len(destacados))}">'
        + (
            "".join(_tarjeta_destacada(tramo) for tramo in destacados)
            if destacados
            else '<div class="highlight-empty">No se identificaron tramos con coincidencia alta.</div>'
        )
        + "</div></div>", unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="detail-shell"><div class="result-panel-heading">{icono("tramos")}<div>'
        '<b>Detalle del recorrido completo</b><span>Todos los tramos del recorrido, en orden.</span>'
        f'</div><span class="detail-heading-count">{len(tramos)} tramos en total</span></div>'
        '<div class="detail-table"><div class="detail-head"><span>#</span><span>Hora</span>'
        '<span>Tramo</span><span>Criticidad estimada</span><span>Clima</span>'
        '<span>Tiempo / distancia</span></div>'
        + "".join(_fila_detalle(tramo) for tramo in tramos)
        + "</div></div>", unsafe_allow_html=True,
    )

    with st.expander(
        "¿Cómo se genera este análisis?", expanded=True, key="result_method"
    ):
        st.markdown(
            f"""
            <p class="method-intro">PrediRuta toma la ruta calculada por Google Maps y analiza
            cada tramo de acuerdo con su hora estimada de paso, el clima previsto y los patrones
            históricos aprendidos por los modelos.</p>
            <div class="method-grid">
              <div class="method-card">
                <div class="method-card-icon">{icono("ubicacion")}</div>
                <div class="method-card-copy"><b>Ruta y tiempos</b><span>Google Maps proporciona
                el recorrido y una duración conservadora con tráfico. PrediRuta usa esos tiempos
                para establecer la hora de paso por cada tramo.</span></div>
              </div>
              <div class="method-card">
                <div class="method-card-icon">{icono("clima")}</div>
                <div class="method-card-copy"><b>Clima previsto</b><span>Para cada tramo se consultan
                las condiciones meteorológicas previstas en su punto medio y para la hora estimada
                en que el usuario pasaría por allí.</span></div>
              </div>
              <div class="method-card">
                <div class="method-card-icon">{icono("barras")}</div>
                <div class="method-card-copy"><b>Comparación histórica</b><span>El modelo evalúa
                ubicación, momento del recorrido y clima para identificar tramos similares a
                escenarios históricos de siniestros.</span></div>
              </div>
              <div class="method-card">
                <div class="method-card-icon">{icono("documento")}</div>
                <div class="method-card-copy"><b>Lectura del resultado</b><span>Una coincidencia
                expresa similitud con patrones aprendidos por el modelo. No representa una
                probabilidad individual de accidente ni modifica la ruta.</span></div>
              </div>
            </div>
            <a class="method-cta" href="?vista=proyecto" target="_self">
              Conoce la metodología, los experimentos y sus resultados →
            </a>
            """,
            unsafe_allow_html=True,
        )


st.session_state.setdefault("resultado", None)
st.session_state.setdefault("consulta", None)

# Descarta resultados de una API anterior. Sin ``ubicacion_tramo`` el frontend
# no puede explicar de forma fiable desde dónde hasta dónde va cada tramo.
if st.session_state.resultado and any(
    "patron_detectado" not in tramo or "ubicacion_tramo" not in tramo
    for tramo in st.session_state.resultado.get("tramos", [])
):
    st.session_state.resultado = None
    st.session_state.consulta = None

vista = st.query_params.get("vista")
if vista == "consulta":
    nueva_consulta()
    st.query_params.clear()
    st.rerun()
elif vista == "proyecto":
    mostrar_informacion_proyecto()
elif st.session_state.resultado:
    mostrar_resultado()
else:
    mostrar_planeacion()
