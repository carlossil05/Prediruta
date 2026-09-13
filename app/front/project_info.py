"""Presentación pública, estática y trazable del proyecto PrediRuta."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


ASSETS = Path(__file__).resolve().parent / "assets" / "project"
REPOSITORIO = "https://github.com/carlossil05/Prediruta"


def _data_uri(nombre: str) -> str:
    """Convierte una figura local en un recurso embebido para el HTML informativo."""

    datos = (ASSETS / nombre).read_bytes()
    return f"data:image/png;base64,{base64.b64encode(datos).decode('ascii')}"


PROJECT_CSS = """
<style>
.block-container{max-width:none!important;padding:0 0 2rem!important}
.project-page{
  --p-navy:#112F49;--p-navy-2:#183B56;--p-teal:#0B8585;--p-teal-dark:#086E71;
  --p-teal-soft:#E8F7F5;--p-blue-soft:#F0F6FA;--p-bg:#F7F9FB;--p-paper:#fff;
  --p-text:#18394F;--p-muted:#647C8D;--p-line:#DDE7EC;--p-line-2:#EBF0F3;
  --p-red:#D94A59;--p-orange:#F1A04C;--p-green:#1A9871;
  --p-shadow:0 18px 44px rgba(17,47,73,.07);--p-max:1280px;--p-radius:22px;
  color:var(--p-text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,
  BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55;
  background:radial-gradient(circle at 8% -5%,rgba(11,133,133,.08),transparent 30rem),
  radial-gradient(circle at 92% 2%,rgba(17,47,73,.05),transparent 32rem),var(--p-bg);
  min-height:100vh;padding-bottom:2rem
}
.project-page *{box-sizing:border-box}.project-page a{color:inherit;text-decoration:none}
.project-page .container{width:min(var(--p-max),calc(100% - 40px));margin-inline:auto}
.project-header{position:sticky;top:0;z-index:50;background:rgba(247,249,251,.93);
  backdrop-filter:blur(16px);border-bottom:1px solid rgba(221,231,236,.9)}
.project-page .topbar{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:18px}
.project-page .brand{display:flex;align-items:center;gap:12px}
.project-page .logo{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;
  background:linear-gradient(145deg,var(--p-teal),#086368);color:#fff;font-size:20px;
  font-weight:900;box-shadow:0 9px 22px rgba(11,133,133,.20)}
.project-page .brand b{display:block;color:var(--p-navy);font-size:19px;letter-spacing:-.02em}
.project-page .brand span{display:block;color:var(--p-muted);font-size:11px}
.project-page .nav{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.project-page .nav a{font-size:12px;color:#587184;padding:8px 9px;border-radius:9px}
.project-page .nav a:hover{background:#fff;color:var(--p-navy)}
.project-page .button{display:inline-flex;align-items:center;justify-content:center;gap:8px;
  min-height:40px;padding:9px 14px;border:1px solid var(--p-line);border-radius:11px;
  background:#fff;color:var(--p-navy);font-size:12px;font-weight:800}
.project-page .button.primary{background:var(--p-teal);color:#fff;border-color:var(--p-teal)}
.project-page .hero{padding:34px 0 18px}.project-page .hero-grid{display:grid;
  grid-template-columns:1.12fr .88fr;gap:18px;align-items:stretch}
.project-page .hero-copy{padding:34px 36px;border-radius:24px;
  background:linear-gradient(135deg,#102F49 0%,#153E5B 64%,#0C7375 150%);
  color:#fff;box-shadow:0 24px 58px rgba(17,47,73,.14)}
.project-page .eyebrow,.project-page .kicker{font-size:12px;font-weight:850;
  letter-spacing:.085em;text-transform:uppercase;color:#89E0DA}
.project-page .hero h1{font-size:clamp(38px,3.5vw,46px);line-height:1.06;
  letter-spacing:-.045em;margin:14px 0 18px;max-width:760px;color:#fff}
.project-page .hero .lead{font-size:15px;color:#D4E1E9;line-height:1.55;margin:0;max-width:760px}
.project-page .hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:25px}
.project-page .hero .button{background:rgba(255,255,255,.08);color:#fff;border-color:rgba(255,255,255,.18)}
.project-page .hero .button.primary{background:#fff;color:var(--p-navy);border-color:#fff}
.project-page .hero-note{margin-top:24px;padding-top:18px;border-top:1px solid rgba(255,255,255,.14);
  font-size:12px;color:#C9D9E3}
.project-page .hero-side{padding:24px;border:1px solid var(--p-line);border-radius:24px;
  background:rgba(255,255,255,.96);box-shadow:var(--p-shadow)}
.project-page .hero-side h2{font-size:20px;line-height:1.2;letter-spacing:-.025em;
  color:var(--p-navy);margin:0}.project-page .hero-side>p{margin:8px 0 16px;
  color:var(--p-muted);font-size:13.5px;line-height:1.5}
.project-page .impact-list{display:grid;gap:10px}.project-page .impact-item{display:grid;
  grid-template-columns:40px 1fr;gap:12px;align-items:start;padding:11px 0;border-top:1px solid var(--p-line-2)}
.project-page .impact-item:first-child{border-top:0;padding-top:0}.project-page .impact-icon{
  width:36px;height:36px;border-radius:11px;display:grid;place-items:center;
  background:var(--p-teal-soft);color:var(--p-teal-dark);font-weight:900}
.project-page .impact-item b{display:block;color:var(--p-navy);font-size:13px}
.project-page .impact-item span{display:block;color:var(--p-muted);font-size:12px;margin-top:3px}
.project-page .magnitude{margin-top:16px;border:1px solid var(--p-line);border-radius:20px;
  background:#fff;display:grid;grid-template-columns:repeat(6,1fr);overflow:hidden}
.project-page .mag{padding:14px 15px;border-left:1px solid var(--p-line-2)}
.project-page .mag:first-child{border-left:0}.project-page .mag strong{display:block;
  font-size:22px;line-height:1;color:var(--p-navy);letter-spacing:-.035em}
.project-page .mag span{display:block;font-size:12px;color:var(--p-muted);margin-top:6px;line-height:1.35}
.project-page section{padding-top:34px}.project-page .section-head{margin-bottom:16px;max-width:930px}
.project-page .kicker{color:var(--p-teal);margin-bottom:7px}.project-page .section-head h2{
  margin:0;font-size:25px;line-height:1.16;color:var(--p-navy);letter-spacing:-.03em}
.project-page .section-head p{margin:7px 0 0;color:var(--p-muted);font-size:13.5px;line-height:1.5}
.project-page .panel{border:1px solid var(--p-line);border-radius:var(--p-radius);
  background:#fff;box-shadow:var(--p-shadow)}
.project-page .value-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.project-page .value-main{padding:28px}.project-page .value-main h3,.project-page .effort-intro h3,
.project-page .dataset-head h3{margin:0;color:var(--p-navy);font-size:20px;letter-spacing:-.02em}
.project-page .value-main p,.project-page .effort-intro p{margin:8px 0 0;color:var(--p-muted);
  font-size:13.5px;line-height:1.5}.project-page .user-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}
.project-page .chip{display:inline-flex;padding:7px 10px;border-radius:999px;background:var(--p-teal-soft);
  color:var(--p-teal-dark);font-size:11px;font-weight:800}.project-page .output-list{margin-top:18px;
  display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.project-page .output{padding:13px;
  border-radius:15px;background:var(--p-blue-soft);border:1px solid #DFEAF1}
.project-page .output b,.project-page .scope-item b{display:block;color:var(--p-navy);font-size:12px}
.project-page .output span,.project-page .scope-item span{display:block;color:var(--p-muted);
  font-size:11px;margin-top:3px}.project-page .scope{padding:27px}.project-page .scope h3,
.project-page .arch-box h3,.project-page .beyond-col h3{margin:0 0 12px;color:var(--p-navy);font-size:21px}
.project-page .scope-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.project-page .scope-item{padding:13px 14px;border:1px solid var(--p-line);border-radius:14px}
.project-page .scope-item span{font-size:12px}.project-page .effort-wrap{padding:29px}
.project-page .effort-intro{display:grid;grid-template-columns:.72fr 1.28fr;gap:20px;align-items:center}
.project-page .big-stat{padding:22px;border-radius:19px;background:var(--p-navy);color:#fff}
.project-page .big-stat strong{display:block;font-size:34px;line-height:1;letter-spacing:-.05em}
.project-page .big-stat span{display:block;font-size:12px;color:#BED0DB;margin-top:8px}
.project-page .sources{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}
.project-page .source{padding:15px;border:1px solid var(--p-line);border-radius:15px}
.project-page .source b,.project-page .control b{display:block;font-size:12px;color:var(--p-navy)}
.project-page .source span,.project-page .control span{display:block;font-size:12px;color:var(--p-muted);margin-top:4px}
.project-page .pipeline{display:grid;grid-template-columns:repeat(6,1fr);gap:9px;margin-top:18px}
.project-page .stage{position:relative;min-height:145px;padding:16px;border:1px solid var(--p-line);
  border-radius:16px;background:#fff}.project-page .stage:after{content:"→";position:absolute;
  right:-9px;top:50%;transform:translateY(-50%);color:#A6B7C2;font-weight:900}
.project-page .stage:last-child:after{display:none}.project-page .stage small{color:var(--p-teal);
  font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.06em}
.project-page .stage b{display:block;font-size:13px;color:var(--p-navy);margin-top:7px}
.project-page .stage p{font-size:12px;color:var(--p-muted);margin:5px 0 0}
.project-page .datasets{display:grid;grid-template-columns:1.22fr .78fr;gap:16px;margin-top:16px}
.project-page .dataset-table{overflow:hidden}.project-page .dataset-head{padding:20px 22px;
  border-bottom:1px solid var(--p-line);display:flex;justify-content:space-between;gap:14px;align-items:end}
.project-page .dataset-head span{font-size:12px;color:var(--p-muted)}.project-page .dataset-row{
  display:grid;grid-template-columns:1.15fr .75fr .48fr .48fr;gap:12px;padding:15px 22px;
  border-bottom:1px solid var(--p-line-2);align-items:center}.project-page .dataset-row:last-child{border-bottom:0}
.project-page .dataset-row.header{background:#F8FAFB;color:#80929F;font-size:11px;font-weight:900;
  text-transform:uppercase;letter-spacing:.05em}.project-page .dataset-row b{font-size:12px;color:var(--p-navy)}
.project-page .dataset-row span{font-size:12px;color:var(--p-muted)}.project-page .controls{padding:22px}
.project-page .controls h3{margin:0 0 12px;color:var(--p-navy);font-size:19px}
.project-page .control-list{display:grid;gap:9px}.project-page .control{display:flex;gap:10px;
  align-items:flex-start;padding:10px 0;border-top:1px solid var(--p-line-2)}
.project-page .control:first-child{border-top:0;padding-top:0}.project-page .check{width:23px;height:23px;
  flex:0 0 23px;border-radius:8px;display:grid;place-items:center;background:var(--p-teal-soft);
  color:var(--p-teal-dark);font-size:11px;font-weight:900}.project-page .control span{margin-top:2px}
.project-page .evidence-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.project-page .figure{border:1px solid var(--p-line);border-radius:19px;background:#fff;overflow:hidden;
  box-shadow:0 10px 26px rgba(17,47,73,.04);margin:0}.project-page .figure-media{height:300px;
  background:#FAFBFC;display:flex;align-items:center;justify-content:center;padding:14px;
  border-bottom:1px solid var(--p-line-2)}.project-page .figure-media img{max-width:100%;max-height:100%;
  object-fit:contain;display:block}.project-page .figure-caption{padding:16px 18px 18px}
.project-page .figure-caption b{font-size:14px;color:var(--p-navy);display:block}
.project-page .figure-caption span{font-size:12px;color:var(--p-muted);display:block;margin-top:5px}
.project-page .model-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px}
.project-page .model-card{padding:20px;border:1px solid var(--p-line);border-radius:18px;background:#fff}
.project-page .badge{display:inline-flex;padding:6px 9px;border-radius:999px;font-size:11px;font-weight:900}
.project-page .badge.core{background:#DDF3F0;color:var(--p-teal-dark)}.project-page .badge.extra{background:#EEF3F7;color:#5D7586}
.project-page .badge.out{background:#FFF0F2;color:#B83C4A}.project-page .model-card h3{margin:12px 0 6px;
  font-size:17px;color:var(--p-navy)}.project-page .model-card p{margin:0;font-size:12px;color:var(--p-muted)}
.project-page .model-card .decision{margin-top:12px;padding-top:11px;border-top:1px dashed var(--p-line);
  font-size:12px;color:#557082}.project-page details.model-detail{border:1px solid var(--p-line);
  border-radius:18px;background:#fff;margin-top:10px;overflow:hidden}
.project-page details.model-detail summary{padding:16px 18px;cursor:pointer;list-style:none;
  display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:13px;
  font-weight:850;color:var(--p-navy)}.project-page details.model-detail summary::-webkit-details-marker{display:none}
.project-page details.model-detail summary::after{content:"＋";font-size:17px;color:var(--p-teal)}
.project-page details.model-detail[open] summary::after{content:"−"}.project-page .detail-body{
  border-top:1px solid var(--p-line);padding:18px;display:grid;grid-template-columns:.9fr 1.1fr;gap:18px}
.project-page .method-list{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:13px}
.project-page .method{padding:10px;border-radius:13px;background:#F7FAFC;border:1px solid var(--p-line);
  font-size:12px;color:#587184}.project-page .detail-copy h4{margin:0;color:var(--p-navy);font-size:17px}
.project-page .detail-copy p{font-size:12px;color:var(--p-muted);margin:6px 0 0}
.project-page .metric-line{display:flex;flex-wrap:wrap;gap:8px;margin-top:13px}.project-page .metric-pill{
  padding:7px 9px;border-radius:10px;background:var(--p-teal-soft);font-size:11px;
  color:var(--p-teal-dark);font-weight:800}.project-page .detail-figures{display:grid;
  grid-template-columns:1fr 1fr;gap:10px}.project-page .detail-fig{height:220px;background:#FAFBFC;
  border:1px solid var(--p-line);border-radius:14px;display:flex;align-items:center;justify-content:center;padding:10px}
.project-page .detail-fig img{max-width:100%;max-height:100%;object-fit:contain}
.project-page .arch,.project-page .beyond-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.project-page .arch-box,.project-page .beyond-col{padding:25px}.project-page .arch-box p,
.project-page .beyond-col>p{font-size:12px;color:var(--p-muted);margin:6px 0 0}
.project-page .arch-flow{margin-top:17px;display:grid;gap:8px}.project-page .arch-step{padding:11px 13px;
  border:1px solid var(--p-line);border-radius:13px;background:#FAFCFD;font-size:12px;color:#567083}
.project-page .arch-step b{color:var(--p-navy)}.project-page .limit-grid{display:grid;
  grid-template-columns:repeat(3,1fr);gap:12px}.project-page .limit{padding:17px;
  border:1px solid var(--p-line);border-radius:17px;background:#fff}.project-page .limit b{
  display:block;font-size:12px;color:var(--p-navy)}.project-page .limit span{display:block;
  font-size:12px;color:var(--p-muted);margin-top:4px}.project-page .reference-grid{display:grid;
  grid-template-columns:repeat(5,1fr);gap:10px}.project-page .reference{padding:16px;
  border:1px solid var(--p-line);border-radius:16px;background:#fff}.project-page .reference b{
  display:block;font-size:12px;color:var(--p-navy)}.project-page .reference span{display:block;
  font-size:11px;color:var(--p-muted);margin:4px 0 10px}.project-page .reference a{font-size:11px;
  color:var(--p-teal-dark);font-weight:850}.project-page .beyond-note{padding:14px 16px;
  border-left:4px solid var(--p-teal);background:var(--p-teal-soft);border-radius:0 14px 14px 0;
  font-size:12px;color:#476779;margin-bottom:14px}.project-page .beyond-col>p{margin-bottom:16px}
.project-page .evol-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.project-page .evol{
  padding:13px;border:1px solid var(--p-line);border-radius:14px;background:#FAFCFD}
.project-page .evol b{display:block;font-size:11px;color:var(--p-navy)}.project-page .evol span{
  display:block;font-size:12px;color:var(--p-muted);margin-top:3px}.project-page .project-footer{
  padding:34px 0 22px;color:#7D919F;font-size:11px;display:flex;justify-content:space-between;
  gap:18px;flex-wrap:wrap;border:0;background:transparent}
@media(max-width:1100px){.project-page .hero-grid,.project-page .value-grid,
  .project-page .effort-intro,.project-page .datasets,.project-page .detail-body,
  .project-page .arch,.project-page .beyond-grid{grid-template-columns:1fr}
  .project-page .magnitude{grid-template-columns:repeat(3,1fr)}.project-page .pipeline{grid-template-columns:repeat(3,1fr)}
  .project-page .stage:after{display:none}.project-page .model-summary{grid-template-columns:1fr}
  .project-page .reference-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:760px){.project-page .container{width:min(calc(100% - 22px),var(--p-max))}
  .project-page .nav a:not(.button){display:none}.project-page .hero{padding-top:22px}
  .project-page .hero-copy{padding:28px 24px}.project-page .hero h1{font-size:34px;line-height:1.08}
  .project-page .hero .lead{font-size:14.5px}.project-page .hero-side{padding:20px}
  .project-page .magnitude{grid-template-columns:repeat(2,1fr)}.project-page section{padding-top:30px}
  .project-page .section-head h2{font-size:23px}.project-page .output-list,.project-page .scope-grid,
  .project-page .sources,.project-page .pipeline,.project-page .evidence-grid,.project-page .limit-grid,
  .project-page .evol-grid,.project-page .reference-grid{grid-template-columns:1fr}
  .project-page .dataset-row{grid-template-columns:1fr;gap:4px}.project-page .dataset-row.header{display:none}
  .project-page .figure-media{height:230px}.project-page .detail-figures{grid-template-columns:1fr}
  .project-page .detail-fig{height:210px}.project-page .method-list{grid-template-columns:1fr}}
</style>
"""


def mostrar_informacion_proyecto() -> None:
    """Renderiza la historia completa del proyecto sin formularios de la consulta."""

    imagenes = {
        "anios": _data_uri("accidentes_por_anio.png"),
        "perimetro": _data_uri("perimetro_urbano.png"),
        "clima": _data_uri("cobertura_clima.png"),
        "zonas": _data_uri("zonas_geograficas.png"),
        "ocurrencia": _data_uri("comparacion_ocurrencia.png"),
        "roc": _data_uri("roc_ocurrencia.png"),
        "estado": _data_uri("comparacion_estado.png"),
        "estado_importancia": _data_uri("importancia_estado.png"),
        "clase": _data_uri("comparacion_clase.png"),
        "clase_matriz": _data_uri("matriz_clase.png"),
    }

    st.markdown(PROJECT_CSS, unsafe_allow_html=True)
    pagina_html = f"""
<div class="project-page">
  <div class="project-header"><div class="container topbar">
    <a class="brand" href="#impacto"><div class="logo">↝</div><div><b>PrediRuta</b><span>Conoce el proyecto</span></div></a>
    <nav class="nav"><a href="#impacto">Impacto</a><a href="#datos">Datos</a>
      <a href="#modelos">Modelos</a><a href="#producto">Producto</a><a href="#futuro">Evolución</a>
      <a class="button primary" href="?vista=consulta" target="_self">Volver a la consulta</a></nav>
  </div></div>
  <main class="container">
    <section class="hero" id="impacto"><div class="hero-grid">
      <div class="hero-copy"><div class="eyebrow">Proyecto aplicado de analítica de datos</div>
        <h1>Una ruta ya te dice por dónde ir. PrediRuta busca ayudarte a entender mejor qué pasa a lo largo del recorrido.</h1>
        <p class="lead">La ruta la calcula Google. PrediRuta toma ese recorrido y analiza cada tramo con base en el lugar, la hora estimada de paso, los patrones históricos de siniestralidad y las condiciones meteorológicas previstas.</p>
        <div class="hero-actions"><a class="button primary" href="?vista=consulta" target="_self">Ver PrediRuta</a>
          <a class="button" href="#datos">Ver todo el trabajo detrás</a></div>
        <div class="hero-note">El resultado es una lectura comparativa de criticidad. No es una probabilidad individual de accidente, no recomienda una ruta y no da instrucciones de conducción.</div>
      </div>
      <aside class="hero-side"><h2>¿Dónde está el impacto?</h2>
        <p>En juntar información que normalmente está separada y llevarla a una lectura que tenga sentido sobre una ruta real.</p>
        <div class="impact-list">
          <div class="impact-item"><div class="impact-icon">↝</div><div><b>De una ruta a una lectura por tramos</b><span>Cada segmento puede interpretarse en su propio contexto.</span></div></div>
          <div class="impact-item"><div class="impact-icon">◷</div><div><b>El momento del recorrido importa</b><span>La hora estimada de paso relaciona cada tramo con su patrón temporal.</span></div></div>
          <div class="impact-item"><div class="impact-icon">☁</div><div><b>El clima deja de estar aislado</b><span>Las condiciones previstas acompañan la lectura histórica y entran al modelo de ocurrencia.</span></div></div>
          <div class="impact-item"><div class="impact-icon">◎</div><div><b>La analítica termina en un producto</b><span>El resultado de los notebooks llega a una consulta visual para el usuario.</span></div></div>
        </div>
      </aside>
    </div>
    <div class="magnitude"><div class="mag"><strong>895.346</strong><span>accidentes finales utilizados</span></div>
      <div class="mag"><strong>5,75 M</strong><span>combinaciones de ocurrencia</span></div>
      <div class="mag"><strong>1,93 M</strong><span>filas en la tabla completa</span></div>
      <div class="mag"><strong>150</strong><span>zonas geográficas de Bogotá</span></div>
      <div class="mag"><strong>325 mil+</strong><span>observaciones meteorológicas</span></div>
      <div class="mag"><strong>3 × 4</strong><span>objetivos × familias de modelos</span></div></div></section>

    <section><div class="section-head"><div class="kicker">Propuesta de valor y usuario</div>
      <h2>La consulta es sencilla. Lo complejo está detrás.</h2>
      <p>El usuario no tiene que entender celdas, clústeres ni métricas. Define el trayecto y el momento; PrediRuta lleva el trabajo analítico a una salida entendible.</p></div>
      <div class="value-grid"><div class="panel value-main"><h3>¿Para quién está pensado?</h3>
        <p>Para quien consulta un desplazamiento en automóvil o motocicleta dentro de Bogotá y quiere revisar el recorrido con más contexto que una ruta y un tiempo estimado.</p>
        <div class="user-row"><span class="chip">Origen</span><span class="chip">Destino</span><span class="chip">Fecha</span><span class="chip">Hora de salida</span></div>
        <div class="output-list"><div class="output"><b>Ruta segmentada</b><span>Google entrega la ruta; PrediRuta la organiza por tramos.</span></div>
          <div class="output"><b>Hora de paso</b><span>Cada tramo se interpreta en el momento previsto.</span></div>
          <div class="output"><b>Clima previsto</b><span>Contexto meteorológico para cada tramo y hora.</span></div></div></div>
        <div class="panel scope"><h3>Actores interesados</h3><div class="scope-grid">
          <div class="scope-item"><b>Conductores</b><span>Comprenden mejor el contexto de su trayecto antes de salir.</span></div>
          <div class="scope-item"><b>Movilidad y seguridad vial</b><span>Complementan diagnósticos con resultados agregados.</span></div>
          <div class="scope-item"><b>Gestores de infraestructura</b><span>Contrastan patrones con operación y señalización.</span></div>
          <div class="scope-item"><b>Academia</b><span>Reproduce datos, experimentos y decisiones analíticas.</span></div>
        </div></div></div>
    </section>

    <section id="datos"><div class="section-head"><div class="kicker">Datos y transformación</div>
      <h2>Antes de entrenar un modelo hubo que convertir una base relacional de movilidad en una estructura espacial, temporal y meteorológica coherente.</h2>
      <p>Esta transformación explica de dónde sale la información que finalmente ve el usuario y por qué el proyecto no es únicamente una interfaz.</p></div>
      <div class="panel effort-wrap"><div class="effort-intro">
        <div class="big-stat"><strong>904.476 → 895.346</strong><span>Registros estructuralmente válidos al inicio y accidentes finales conservados.</span></div>
        <div><h3>No fue una sola limpieza</h3><p>Se revisaron estructura, llaves, granularidad, periodo, coordenadas, perímetro urbano, relaciones, categorías, datos faltantes, clima y trazabilidad. Luego se construyó un dataset específico para cada pregunta.</p></div>
      </div><div class="sources"><div class="source"><b>Secretaría Distrital de Movilidad</b><span>Accidentes, vías, actores, vehículos y causas.</span></div>
        <div class="source"><b>ERA5 + ECMWF IFS / Open-Meteo</b><span>Clima histórico por ubicación y momento.</span></div>
        <div class="source"><b>Google Maps Platform</b><span>Ruta, geometría, distancia y duración de consulta.</span></div></div>
      <div class="pipeline"><div class="stage"><small>Base</small><b>Depuración relacional</b><p>Llaves, duplicados, vías, actores, vehículos y causas.</p></div>
        <div class="stage"><small>Alcance</small><b>Periodo y Bogotá urbana</b><p>Perímetro, coordenadas y reglas de inclusión.</p></div>
        <div class="stage"><small>Espacio</small><b>Celdas de 500 m</b><p>EPSG:3116 y consolidación celda–hora.</p></div>
        <div class="stage"><small>Zonas</small><b>150 grupos geográficos</b><p>MiniBatchKMeans reutilizado por los modelos.</p></div>
        <div class="stage"><small>Clima</small><b>Asignación meteorológica</b><p>ERA5 antes de 2017 y ECMWF IFS desde 2017.</p></div>
        <div class="stage"><small>Salida</small><b>Datasets analíticos</b><p>Unidades distintas para ocurrencia, eventos y actores.</p></div></div></div>
      <div class="datasets"><div class="panel dataset-table"><div class="dataset-head"><h3>Productos de datos construidos</h3><span>Cada modelo requiere su propia unidad.</span></div>
        <div class="dataset-row header"><span>Producto</span><span>Unidad</span><span>Filas</span><span>Columnas</span></div>
        <div class="dataset-row"><b>DATASET_OCURRENCIA</b><span>Año–zona–mes–día–hora</span><span>5.745.600</span><span>17</span></div>
        <div class="dataset-row"><b>DATASET_EVENTOS</b><span>Accidente</span><span>895.346</span><span>23</span></div>
        <div class="dataset-row"><b>TABLA_COMPLETA_MODELADO</b><span>Actor / accidente sin actor</span><span>1.928.614</span><span>47</span></div>
        <div class="dataset-row"><b>DICCIONARIO_CATEGORIAS</b><span>Código–categoría</span><span>237</span><span>4</span></div></div>
        <aside class="panel controls"><h3>Controles antes de modelar</h3><div class="control-list">
          <div class="control"><div class="check">✓</div><div><b>Integridad entre tablas</b><span>Sin accidentes huérfanos y con claves únicas.</span></div></div>
          <div class="control"><div class="check">✓</div><div><b>Clima consistente</b><span>ERA5 e IFS separados según el periodo.</span></div></div>
          <div class="control"><div class="check">✓</div><div><b>Misma lógica espacial</b><span>Los tres objetivos reutilizan 150 zonas.</span></div></div>
          <div class="control"><div class="check">✓</div><div><b>Trazabilidad</b><span>Identificadores conservados, nunca usados como predictores.</span></div></div>
        </div></aside></div>
    </section>

    <section id="evidencia"><div class="section-head"><div class="kicker">Evidencias de los notebooks</div>
      <h2>Las gráficas que explican las decisiones centrales de la preparación.</h2>
      <p>Periodo, perímetro, cobertura meteorológica y representación espacial se validaron antes de modelar.</p></div>
      <div class="evidence-grid">
        <figure class="figure"><div class="figure-media"><img src="{imagenes['anios']}" alt="Accidentes registrados por año"></div><figcaption class="figure-caption"><b>Selección del periodo histórico</b><span>La distribución anual justificó el inicio del periodo útil y evitó mezclar años con coberturas diferentes.</span></figcaption></figure>
        <figure class="figure"><div class="figure-media"><img src="{imagenes['perimetro']}" alt="Accidentes dentro del perímetro urbano"></div><figcaption class="figure-caption"><b>Validación espacial</b><span>Los registros utilizados se contrastaron con el perímetro urbano definido.</span></figcaption></figure>
        <figure class="figure"><div class="figure-media"><img src="{imagenes['clima']}" alt="Cobertura meteorológica sobre Bogotá"></div><figcaption class="figure-caption"><b>Integración meteorológica</b><span>La cobertura exigió una lógica diferenciada antes y después de 2017.</span></figcaption></figure>
        <figure class="figure"><div class="figure-media"><img src="{imagenes['zonas']}" alt="Distribución de las 150 zonas"></div><figcaption class="figure-caption"><b>Referencia espacial común</b><span>Las 150 zonas reducen la complejidad y se reutilizan entre los modelos.</span></figcaption></figure>
      </div>
    </section>

    <section id="modelos"><div class="section-head"><div class="kicker">Experimentación analítica</div>
      <h2>Modelar fue mucho más que escoger el algoritmo con el número más alto.</h2>
      <p>Se revisaron distribuciones, escenarios de variables, desbalance, hiperparámetros y generalización temporal. Los resultados productivos corresponden a los artefactos exportados en <b>modelo/modelos_produccion</b>.</p></div>
      <div class="model-summary"><div class="model-card"><span class="badge core">Núcleo del MVP</span><h3>Ocurrencia relativa</h3><p>Identifica combinaciones de zona y momento similares a patrones históricos de ocurrencia.</p><div class="decision"><strong>Decisión:</strong> MLP con clima para la señal comparativa.</div></div>
        <div class="model-card"><span class="badge extra">Análisis complementario</span><h3>Estado del actor</h3><p>Evalúa HERIDO, ILESO y MUERTO solo bajo la condición de que ocurriera un siniestro.</p><div class="decision"><strong>Decisión:</strong> XGBoost operativo sin clima.</div></div>
        <div class="model-card"><span class="badge out">Resultado experimental</span><h3>Clase de accidente</h3><p>Se estudió ATROPELLO, CHOQUE y OTROS, pero la señal no respaldó llevarlo al producto.</p><div class="decision"><strong>Decisión:</strong> documentar y no incorporar al MVP.</div></div></div>
      <details class="model-detail" open><summary>Modelo de ocurrencia · qué se probó y por qué quedó en el MVP</summary><div class="detail-body">
        <div class="detail-copy"><h4>Comparación sobre periodos futuros</h4><p>Regresión logística, Random Forest, XGBoost y MLP se compararon con y sin clima. La selección se hizo en validación temporal y se confirmó en años aislados.</p>
          <div class="method-list"><div class="method">Línea base</div><div class="method">Umbral validado</div><div class="method">4 familias</div><div class="method">Con / sin clima</div><div class="method">Prueba temporal</div><div class="method">ROC + Precision-Recall</div></div>
          <div class="metric-line"><span class="metric-pill">ROC-AUC prueba: 0,6308</span><span class="metric-pill">Balanced Accuracy: 0,5981</span><span class="metric-pill">Recall: 0,6920</span><span class="metric-pill">Umbral: 0,3090</span></div>
          <p style="margin-top:12px">La baja precisión y el cambio temporal explican por qué el score no se presenta como una probabilidad individual.</p></div>
        <div class="detail-figures"><div class="detail-fig"><img src="{imagenes['ocurrencia']}" alt="Comparación de modelos de ocurrencia"></div><div class="detail-fig"><img src="{imagenes['roc']}" alt="Curva ROC final de ocurrencia"></div></div></div></details>
      <details class="model-detail"><summary>Modelo de estado · validación y variables que más aportan</summary><div class="detail-body">
        <div class="detail-copy"><h4>Escenario disponible antes del viaje</h4><p>Se separaron escenarios completos y operativos para no depender de información que solo existe después del accidente. También se revisó estabilidad, incertidumbre y desempeño por clase.</p>
          <div class="method-list"><div class="method">Completo / operativo</div><div class="method">Con / sin clima</div><div class="method">Bootstrap pareado</div><div class="method">Backtesting temporal</div><div class="method">Diagnóstico por clase</div><div class="method">Importancia por permutación</div></div>
          <div class="metric-line"><span class="metric-pill">F1 macro prueba: 0,5688</span><span class="metric-pill">Balanced Accuracy: 0,5926</span><span class="metric-pill">HERIDO F1: 0,831</span></div><p style="margin-top:12px">MUERTO sigue siendo la clase más difícil de identificar.</p></div>
        <div class="detail-figures"><div class="detail-fig"><img src="{imagenes['estado']}" alt="Comparación de modelos de estado"></div><div class="detail-fig"><img src="{imagenes['estado_importancia']}" alt="Importancia de variables del modelo de estado"></div></div></div></details>
      <details class="model-detail"><summary>Modelo de clase de accidente · por qué no se llevó al producto</summary><div class="detail-body">
        <div class="detail-copy"><h4>Un experimento útil, aunque no terminara en el MVP</h4><p>Se compararon escenarios completos y operativos, versiones con y sin clima y las mismas familias. CHOQUE se reconoce mucho mejor que ATROPELLO y OTROS.</p>
          <div class="method-list"><div class="method">Agrupación de clases</div><div class="method">4 familias</div><div class="method">Bootstrap pareado</div><div class="method">Backtesting temporal</div><div class="method">Confusión normalizada</div><div class="method">Sensibilidad de partición</div></div>
          <div class="metric-line"><span class="metric-pill">F1 macro prueba: 0,3735</span><span class="metric-pill">Balanced Accuracy: 0,3871</span><span class="metric-pill">CHOQUE ≈ 80 % identificado</span></div><p style="margin-top:12px">No se muestra una salida que todavía no tiene suficiente respaldo para las clases minoritarias.</p></div>
        <div class="detail-figures"><div class="detail-fig"><img src="{imagenes['clase']}" alt="Comparación de modelos de clase"></div><div class="detail-fig"><img src="{imagenes['clase_matriz']}" alt="Matriz de confusión del modelo de clase"></div></div></div></details>
    </section>

    <section id="producto"><div class="section-head"><div class="kicker">Del notebook a la aplicación</div>
      <h2>PrediRuta separa el flujo que construye el conocimiento del flujo que lo usa durante una consulta.</h2>
      <p>El front es la última capa de un proceso reproducible que conserva datos, transformaciones, modelos y metadatos.</p></div>
      <div class="arch"><div class="panel arch-box"><h3>Flujo histórico · offline</h3><p>Prepara los datos, entrena y valida.</p><div class="arch-flow">
        <div class="arch-step"><b>SDM + clima histórico</b> → limpieza, relaciones y calidad.</div><div class="arch-step"><b>Transformación espacial y temporal</b> → celdas, zonas y datasets.</div><div class="arch-step"><b>Experimentación</b> → escenarios, modelos y análisis de errores.</div><div class="arch-step"><b>Artefactos</b> → pipelines, metadatos y centroides para inferencia.</div></div></div>
        <div class="panel arch-box"><h3>Flujo de consulta · online</h3><p>Se ejecuta cuando una persona analiza su trayecto.</p><div class="arch-flow">
          <div class="arch-step"><b>Origen + destino + fecha + hora</b> → entrada del usuario.</div><div class="arch-step"><b>Google Maps</b> → ruta, geometría, distancia y duración conservadora con tráfico.</div><div class="arch-step"><b>PrediRuta</b> → tramos, zona, hora de paso e inferencia.</div><div class="arch-step"><b>Clima previsto + mapa</b> → contexto meteorológico y visualización.</div></div></div></div>
    </section>

    <section id="limites"><div class="section-head"><div class="kicker">Alcances y límites</div>
      <h2>Las limitaciones también forman parte del proyecto.</h2><p>Hacen explícito cómo debe interpretarse el resultado y qué no puede concluirse.</p></div>
      <div class="limit-grid"><div class="limit"><b>Cobertura</b><span>La versión actual analiza la zona urbana de Bogotá incluida en el entrenamiento.</span></div>
        <div class="limit"><b>Exposición desconocida</b><span>Sin denominador de vehículos expuestos, el score no es una probabilidad individual.</span></div>
        <div class="limit"><b>Deriva temporal</b><span>Los patrones cambian y requieren monitoreo y reentrenamiento.</span></div>
        <div class="limit"><b>Resolución meteorológica</b><span>El clima representa un sector y un momento, no cada cuadra.</span></div>
        <div class="limit"><b>Dependencia de APIs</b><span>Ruta, tiempos y pronóstico dependen de servicios externos.</span></div>
        <div class="limit"><b>Interpretación del color</b><span>Un nivel bajo no significa “sin riesgo”; solo menor similitud relativa.</span></div></div>
    </section>

    <section id="fuentes"><div class="section-head"><div class="kicker">Fuentes y trazabilidad</div>
      <h2>Los datos, notebooks y artefactos pueden rastrearse.</h2><p>Las fuentes externas se complementan con el repositorio que documenta la preparación, los experimentos y la aplicación.</p></div>
      <div class="reference-grid"><div class="reference"><b>Siniestralidad vial</b><span>Secretaría Distrital de Movilidad.</span><a href="https://datos.movilidadbogota.gov.co/" target="_blank" rel="noopener">Consultar fuente ↗</a></div>
        <div class="reference"><b>Perímetro urbano</b><span>Datos Abiertos Bogotá.</span><a href="https://datosabiertos.bogota.gov.co/dataset/perimetro-urbano-bogota-d-c" target="_blank" rel="noopener">Consultar fuente ↗</a></div>
        <div class="reference"><b>Clima histórico</b><span>ERA5 / ECMWF vía Open-Meteo.</span><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noopener">Consultar fuente ↗</a></div>
        <div class="reference"><b>Rutas y tiempos</b><span>Google Maps Platform.</span><a href="https://developers.google.com/maps/documentation/routes" target="_blank" rel="noopener">Consultar fuente ↗</a></div>
        <div class="reference"><b>Repositorio</b><span>Notebooks, API, front y modelos.</span><a href="{REPOSITORIO}" target="_blank" rel="noopener">Ver código en GitHub ↗</a></div></div>
    </section>

    <section id="futuro"><div class="section-head"><div class="kicker">Después del MVP actual</div>
      <h2>Una siguiente etapa puede crecer en producto, datos y operación.</h2><p>Estas líneas pertenecen a una evolución posterior; no son faltantes de la entrega actual.</p></div>
      <div class="beyond-note"><strong>Importante:</strong> el alcance actual ya entrega una consulta completa. Lo siguiente son oportunidades de evolución.</div>
      <div class="beyond-grid"><div class="panel beyond-col"><h3>Siguiente etapa del MVP</h3><p>Consolidar el producto construido.</p><div class="evol-grid">
        <div class="evol"><b>Validación con usuarios</b><span>Comprobar lenguaje, colores y jerarquía.</span></div><div class="evol"><b>Monitoreo</b><span>Definir deriva y criterios de reentrenamiento.</span></div><div class="evol"><b>Integraciones robustas</b><span>Fortalecer fallos, reintentos y trazabilidad.</span></div><div class="evol"><b>Gobierno del dato</b><span>Versionar insumos, esquemas y modelos.</span></div></div></div>
        <div class="panel beyond-col"><h3>Posibles evolutivos</h3><p>Capacidades posteriores a la validación.</p><div class="evol-grid">
          <div class="evol"><b>Comparar horarios</b><span>Contrastar el mismo recorrido en diferentes momentos.</span></div><div class="evol"><b>Datos de exposición</b><span>Incorporar volumen vehicular.</span></div><div class="evol"><b>Vista institucional</b><span>Explorar patrones agregados por zona y momento.</span></div><div class="evol"><b>Mayor resolución</b><span>Evaluar nuevas fuentes de contexto.</span></div></div></div></div>
    </section>
    <div class="project-footer"><div>PrediRuta · Proyecto aplicado de analítica de datos<br>Lizeth García · Carlos Silva · Leonardo Guzman</div><div>Ruta: Google Maps · Análisis: PrediRuta · Sin recomendaciones de conducción</div></div>
  </main>
</div>
"""
    # Markdown termina un bloque HTML al encontrar una línea vacía. Como toda la
    # página vive dentro del mismo contenedor, retirarlas evita que las secciones
    # posteriores aparezcan como código en lugar de componentes visuales.
    pagina_html = "\n".join(
        linea for linea in pagina_html.splitlines() if linea.strip()
    )
    st.markdown(pagina_html, unsafe_allow_html=True)
