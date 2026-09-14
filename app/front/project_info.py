"""Presentación pública, estática y trazable del proyecto PrediRuta."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


ASSETS = Path(__file__).resolve().parent / "assets" / "project"
BRAND_ICON = Path(__file__).resolve().parent / "assets" / "prediruta-icon.png"
REPOSITORIO = "https://github.com/carlossil05/Prediruta"


def _data_uri(nombre: str) -> str:
    """Convierte una figura local en un recurso embebido para el HTML informativo."""

    datos = (ASSETS / nombre).read_bytes()
    return f"data:image/png;base64,{base64.b64encode(datos).decode('ascii')}"


def icono_marca() -> str:
    """Entrega el icono oficial embebido para todos los encabezados."""

    datos = base64.b64encode(BRAND_ICON.read_bytes()).decode("ascii")
    return f'<img src="data:image/png;base64,{datos}" alt="Icono de PrediRuta">'


def _icono_impacto(nombre: str) -> str:
    """Devuelve un icono SVG ligero para las tarjetas del panel de impacto."""

    trazos = {
        "vehiculo": (
            '<path d="M5 17h14v-5l-2-5H7l-2 5v5Z"/>'
            '<path d="M7 7 5 4M17 7l2-3M7.5 13h.01M16.5 13h.01M7 17v2M17 17v2"/>'
        ),
        "escudo": (
            '<path d="M12 3 20 6v5c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6l8-3Z"/>'
            '<path d="M12 3v18"/>'
        ),
        "via": '<path d="M8 3 4 21M16 3l4 18M12 4v4M12 11v4M12 18v2"/>',
        "academia": (
            '<path d="m3 9 9-5 9 5-9 5-9-5Z"/>'
            '<path d="M7 12v5c3 2 7 2 10 0v-5M21 9v6"/>'
        ),
    }
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{trazos[nombre]}</svg>'
    )


def _icono_flujo(nombre: str) -> str:
    """Devuelve iconos lineales para explicar el paso del notebook al producto."""

    trazos = {
        "datos": (
            '<ellipse cx="12" cy="5" rx="7" ry="3"/>'
            '<path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>'
        ),
        "ajustes": (
            '<circle cx="12" cy="12" r="3"/>'
            '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/>'
        ),
        "espacio": (
            '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/>'
            '<path d="M9 3v15M15 6v15"/><circle cx="12" cy="10" r="2"/>'
        ),
        "barras": '<path d="M5 20v-6M10 20V9M15 20V4M20 20v-9"/>',
        "cubo": '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
        "documento": '<path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v5h4M9 12h6M9 16h6"/>',
        "etiqueta": '<path d="M3 12 12 3h7l2 2v7l-9 9-9-9Z"/><circle cx="16.5" cy="7.5" r="1"/>',
        "usuario": '<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
        "ruta": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h4a3 3 0 0 0 3-3V9M15 9l3-3"/>',
        "nube": '<path d="M7 18h10a4 4 0 0 0 .7-7.9A6 6 0 0 0 6.3 8.5 4.8 4.8 0 0 0 7 18Z"/>',
        "estrella": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3Z"/>',
    }
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{trazos[nombre]}</svg>'
    )


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
.project-page .logo img{border-radius:inherit;display:block;height:100%;object-fit:cover;width:100%}
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
.project-page .hero-copy,.project-page .hero-side{height:100%}.project-page .hero-side{
  background:rgba(255,255,255,.96);border:1px solid var(--p-line);border-radius:24px;
  box-shadow:var(--p-shadow);display:flex;flex-direction:column;padding:24px}
.project-page .hero-side h2{font-size:20px;line-height:1.2;letter-spacing:-.025em;
  color:var(--p-navy);margin:0}.project-page .hero-side>p{margin:8px 0 16px;
  color:var(--p-muted);font-size:13.5px;line-height:1.5}
.project-page .impact-list{display:grid;gap:10px;grid-template-columns:1fr 1fr}
.project-page .impact-item{align-content:start;border:1px solid var(--p-line);border-radius:14px;
  display:grid;min-height:132px;padding:12px}.project-page .impact-icon{align-items:center;
  background:var(--p-teal-soft);border-radius:10px;color:var(--p-teal-dark);display:flex;
  height:36px;justify-content:center;margin-bottom:8px;width:36px}
.project-page .impact-icon svg{height:20px;stroke:currentColor;stroke-width:1.9;width:20px}
.project-page .impact-item b{color:var(--p-navy);display:block;font-size:12px;line-height:1.3}
.project-page .impact-item span{color:var(--p-muted);display:block;font-size:11px;line-height:1.4;margin-top:4px}
.project-page .hero-impact-note{align-items:center;background:linear-gradient(90deg,#eef7f8,#f8fbfc);
  border-radius:12px;color:var(--p-muted);display:grid;font-size:10.5px;gap:10px;
  grid-template-columns:26px 1fr;line-height:1.4;margin-top:auto;padding:9px 11px}
.project-page .hero-impact-note i{align-items:center;border:1.5px solid #4fa5a8;border-radius:50%;
  color:var(--p-teal);display:flex;font-style:normal;font-weight:850;height:22px;
  justify-content:center;width:22px}
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
.project-page .value-section .section-head{max-width:1080px;margin-bottom:20px}
.project-page .value-section .section-head h2{font-size:30px}.project-page .value-section .section-head p{
  font-size:15px}.project-page .value-grid{align-items:stretch;display:grid;
  grid-template-columns:1fr 1fr;gap:16px}
.project-page .value-main,.project-page .value-impact{display:flex;flex-direction:column;
  min-height:0;padding:24px 26px}
.project-page .value-main h3,.project-page .value-impact h3,.project-page .effort-intro h3{
  margin:0;color:var(--p-navy);font-size:20px;letter-spacing:-.02em}
.project-page .value-main>p,.project-page .value-impact>p,.project-page .effort-intro p{margin:8px 0 0;color:var(--p-muted);
  font-size:13.5px;line-height:1.5}.project-page .user-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}
.project-page .chip{display:inline-flex;padding:7px 10px;border-radius:999px;background:var(--p-teal-soft);
  color:var(--p-teal-dark);font-size:11px;font-weight:800}.project-page .output-list{margin-top:18px;
  display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.project-page .output{padding:13px;
  border-radius:15px;background:var(--p-blue-soft);border:1px solid #DFEAF1}
.project-page .output b{display:block;color:var(--p-navy);font-size:12px}
.project-page .output span{display:block;color:var(--p-muted);font-size:11px;margin-top:3px}
.project-page .value-points{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:13px}
.project-page .value-point{border:1px solid var(--p-line);border-radius:13px;min-height:68px;padding:10px 12px}
.project-page .value-point b{color:var(--p-navy);display:block;font-size:12px;line-height:1.25}
.project-page .value-point span{color:var(--p-muted);display:block;font-size:11px;line-height:1.35;margin-top:3px}
.project-page .value-disclaimer{color:#718796;font-size:11.5px;font-style:italic;
  margin-top:11px;padding-top:0}
.project-page .arch-box h3{margin:0 0 12px;color:var(--p-navy);font-size:21px}
.project-page .beyond-col h3{margin:0;color:var(--p-navy);font-size:17px}
.project-page .effort-wrap{padding:29px}
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
.project-page .dataset-head h3,.project-page .controls h3{color:var(--p-navy);font-size:19px;
  font-weight:700;letter-spacing:normal;line-height:1.25}.project-page .dataset-head h3{margin:0}
.project-page .controls h3{margin:0 0 12px}
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
  min-height:64px}.project-page .method b{display:block;color:var(--p-navy);font-size:11px;
  line-height:1.25;margin-bottom:4px}.project-page .method span{display:block;color:#587184;font-size:11px;
  line-height:1.4}.project-page .detail-copy h4{margin:0;color:var(--p-navy);font-size:17px}
.project-page .detail-copy p{font-size:12px;color:var(--p-muted);margin:6px 0 0}
.project-page .metric-line{display:flex;flex-wrap:wrap;gap:8px;margin-top:13px}.project-page .metric-pill{
  padding:7px 9px;border-radius:10px;background:var(--p-teal-soft);font-size:11px;
  color:var(--p-teal-dark);font-weight:800}.project-page .detail-visuals{display:flex;flex-direction:column;
  min-width:0}.project-page .model-reading{background:#F2FAF9;border-left:3px solid var(--p-teal);
  border-radius:0 10px 10px 0;color:#466779!important;font-size:12px;line-height:1.5;
  margin:10px 0 0!important;padding:11px 12px}.project-page .model-reading.warning{border-left-color:var(--p-red);
  background:#FFF7F8}.project-page .detail-figures{display:grid;
  grid-template-columns:1fr 1fr;gap:10px}.project-page .detail-fig{height:220px;background:#FAFBFC;
  border:1px solid var(--p-line);border-radius:14px;display:flex;align-items:center;justify-content:center;padding:10px}
.project-page .detail-fig img{max-width:100%;max-height:100%;object-fit:contain}
.project-page .flow-system{display:grid;grid-template-columns:1.1fr 28px .84fr 28px 1.06fr;
  gap:10px;align-items:stretch}.project-page .flow-card{background:#fff;border:1px solid var(--p-line);
  border-radius:20px;box-shadow:0 10px 28px rgba(17,47,73,.04);display:flex;flex-direction:column;
  min-width:0;padding:18px}.project-page .flow-card h3{color:var(--p-navy);font-size:17px;
  line-height:1.25;margin:0}.project-page .flow-card>p{color:var(--p-muted);font-size:11.5px;
  line-height:1.4;margin:4px 0 12px}.project-page .flow-items{display:grid;gap:7px}
.project-page .flow-item{align-items:center;background:linear-gradient(100deg,#FBFDFE,#F8FBFD);
  border:1px solid var(--p-line);border-radius:13px;display:flex;gap:10px;min-height:55px;
  padding:7px 9px}.project-page .flow-item-icon{align-items:center;background:linear-gradient(145deg,#F4FBFC,#EEF5FA);
  border:1px solid #E5EEF2;border-radius:11px;color:#1268B4;display:flex;flex:0 0 38px;height:38px;
  justify-content:center;width:38px}.project-page .flow-item-icon svg{height:23px;width:23px}
.project-page .flow-copy{align-items:center;display:grid;gap:8px;grid-template-columns:minmax(112px,.72fr) minmax(0,1.28fr);
  min-width:0;width:100%}.project-page .flow-copy b{color:var(--p-navy);font-size:11px;line-height:1.28}
.project-page .flow-copy span{color:#557086;font-size:10.5px;line-height:1.34}
.project-page .flow-card.artifacts .flow-copy{display:block}.project-page .flow-card.artifacts .flow-copy span{
  display:block;margin-top:1px}.project-page .flow-connector{align-items:center;color:#7893A5;display:flex;
  font-size:33px;font-weight:500;justify-content:center}.project-page .flow-checks{display:flex;gap:7px;
  margin-top:auto;padding-top:12px}.project-page .flow-check{align-items:center;background:#F0FAF9;border:1px solid #D8EFEC;
  border-radius:999px;color:var(--p-navy-2);display:flex;flex:1;font-size:9.5px;gap:6px;
  justify-content:center;line-height:1.2;min-height:32px;padding:6px 7px;text-align:center}
.project-page .flow-check i{align-items:center;background:#29A59B;border-radius:50%;color:#fff;display:flex;
  flex:0 0 14px;font-size:9px;font-style:normal;font-weight:900;height:14px;justify-content:center;width:14px}
.project-page .flow-note{align-items:center;background:linear-gradient(100deg,#EEF9F8,#F3FBFC);
  border:1px solid #CEE8E5;border-radius:12px;color:var(--p-navy);display:flex;font-size:10.5px;
  font-weight:750;gap:10px;line-height:1.35;margin-top:auto;padding:10px}
.project-page .flow-note i{align-items:center;background:#2FA69E;border-radius:50%;color:#fff;display:flex;
  flex:0 0 25px;font-size:14px;font-style:normal;font-weight:850;height:25px;justify-content:center;width:25px}
.project-page .flow-value{align-items:center;background:linear-gradient(90deg,#FAFCFF,#F4F9FF);
  border:1px solid #DCE8F1;border-radius:14px;color:#58758B;display:flex;font-size:11.5px;gap:12px;
  margin-top:12px;padding:11px 14px}.project-page .flow-value svg{color:#1769B3;flex:0 0 20px;height:20px;width:20px}
.project-page .flow-value b{color:var(--p-navy)}.project-page .future-section{padding-top:28px}
.project-page .future-section .section-head{margin-bottom:11px;max-width:1120px}
.project-page .future-section .section-head .kicker{margin-bottom:4px}
.project-page .future-section .section-head h2{font-size:23px}.project-page .future-section .section-head p{
  font-size:12.5px;line-height:1.42;margin-top:5px}.project-page .beyond-grid{align-items:start;display:grid;
  grid-template-columns:1fr 1fr;gap:13px}.project-page .beyond-col{padding:17px 19px}
.project-page .beyond-col>p{font-size:11.5px;color:var(--p-muted);margin:3px 0 10px}.project-page .limit-grid{display:grid;
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
  font-size:12px;color:#476779;margin-bottom:14px}.project-page .evol-grid{display:grid;
  grid-template-columns:1fr 1fr;gap:7px}.project-page .evol{min-height:66px;padding:9px 11px;
  border:1px solid var(--p-line);border-radius:12px;background:#FAFCFD}
.project-page .evol b{display:block;font-size:11px;color:var(--p-navy)}.project-page .evol span{
  display:block;font-size:10.5px;color:var(--p-muted);line-height:1.35;margin-top:2px}.project-page .project-footer{
  padding:34px 0 22px;color:#7D919F;font-size:11px;display:flex;justify-content:space-between;
  gap:18px;flex-wrap:wrap;border:0;background:transparent}
@media(max-width:1100px){.project-page .hero-grid,.project-page .value-grid,
  .project-page .effort-intro,.project-page .datasets,.project-page .detail-body,
  .project-page .beyond-grid{grid-template-columns:1fr}
  .project-page .flow-system{grid-template-columns:1fr}.project-page .flow-connector{height:26px;transform:rotate(90deg)}
  .project-page .flow-copy{grid-template-columns:minmax(145px,.55fr) minmax(0,1.45fr)}
  .project-page .flow-card.artifacts .flow-copy{display:grid}
  .project-page .value-main,.project-page .value-impact{min-height:0}
  .project-page .magnitude{grid-template-columns:repeat(3,1fr)}.project-page .pipeline{grid-template-columns:repeat(3,1fr)}
  .project-page .stage:after{display:none}.project-page .model-summary{grid-template-columns:1fr}
  .project-page .reference-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:760px){.project-page .container{width:min(calc(100% - 22px),var(--p-max))}
  .project-page .nav a:not(.button){display:none}.project-page .hero{padding-top:22px}
  .project-page .hero-copy{padding:28px 24px}.project-page .hero h1{font-size:34px;line-height:1.08}
  .project-page .hero .lead{font-size:14.5px}.project-page .hero-side{padding:20px}
  .project-page .impact-list{grid-template-columns:1fr}.project-page .impact-item{min-height:0}
  .project-page .magnitude{grid-template-columns:repeat(2,1fr)}.project-page section{padding-top:30px}
  .project-page .section-head h2,.project-page .value-section .section-head h2{font-size:23px}
  .project-page .output-list,.project-page .value-points,
  .project-page .sources,.project-page .pipeline,.project-page .evidence-grid,.project-page .limit-grid,
  .project-page .evol-grid,.project-page .reference-grid{grid-template-columns:1fr}
  .project-page .dataset-row{grid-template-columns:1fr;gap:4px}.project-page .dataset-row.header{display:none}
  .project-page .figure-media{height:230px}.project-page .detail-figures{grid-template-columns:1fr}
  .project-page .detail-fig{height:210px}.project-page .method-list{grid-template-columns:1fr}
  .project-page .flow-card{padding:15px}.project-page .flow-copy,
  .project-page .flow-card.artifacts .flow-copy{display:block}.project-page .flow-copy span{display:block;margin-top:2px}
  .project-page .flow-checks{flex-wrap:wrap}.project-page .flow-check{flex:1 1 135px}.project-page .flow-value{align-items:flex-start}}
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
    <a class="brand" href="#impacto"><div class="logo">{icono_marca()}</div><div><b>PrediRuta</b><span>Conoce el proyecto</span></div></a>
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
          <a class="button" href="{REPOSITORIO}" target="_blank" rel="noopener noreferrer">Ver repositorio en GitHub ↗</a></div>
        <div class="hero-note">El resultado es una lectura comparativa de criticidad. No es una probabilidad individual de accidente, no recomienda una ruta y no da instrucciones de conducción.</div>
      </div>
      <aside class="hero-side"><h2>¿Dónde está el impacto?</h2>
        <p>PrediRuta convierte información histórica, temporal y climática en una lectura por tramos que puede ser útil para distintos actores.</p>
        <div class="impact-list">
          <div class="impact-item"><div class="impact-icon">{_icono_impacto("vehiculo")}</div><div><b>Conductores</b><span>Comprenden mejor el contexto de su trayecto antes de salir y pueden identificar tramos que requieren mayor atención durante el recorrido.</span></div></div>
          <div class="impact-item"><div class="impact-icon">{_icono_impacto("escudo")}</div><div><b>Movilidad y seguridad vial</b><span>Complementan diagnósticos con resultados agregados y pueden identificar patrones recurrentes para fortalecer análisis preventivos.</span></div></div>
          <div class="impact-item"><div class="impact-icon">{_icono_impacto("via")}</div><div><b>Gestores de infraestructura</b><span>Contrastan patrones con la operación, el estado de la vía y la señalización para revisar puntos que merecen análisis adicional.</span></div></div>
          <div class="impact-item"><div class="impact-icon">{_icono_impacto("academia")}</div><div><b>Academia</b><span>Reproduce datos, experimentos y decisiones analíticas, facilitando la validación y mejora de la metodología.</span></div></div>
        </div>
        <div class="hero-impact-note"><i>i</i><span>PrediRuta no recomienda rutas; entrega una lectura de criticidad por tramos para apoyar la interpretación.</span></div>
      </aside>
    </div>
    <div class="magnitude"><div class="mag"><strong>895.346</strong><span>accidentes finales utilizados</span></div>
      <div class="mag"><strong>5,75 M</strong><span>combinaciones de ocurrencia</span></div>
      <div class="mag"><strong>1,93 M</strong><span>filas en la tabla completa</span></div>
      <div class="mag"><strong>150</strong><span>zonas geográficas de Bogotá</span></div>
      <div class="mag"><strong>325 mil+</strong><span>observaciones meteorológicas</span></div>
      <div class="mag"><strong>3 × 4</strong><span>objetivos × familias de modelos</span></div></div></section>

    <section class="value-section"><div class="section-head"><div class="kicker">Propuesta de valor y usuario</div>
      <h2>La consulta es sencilla. Lo complejo está detrás.</h2>
      <p>El usuario no tiene que entender celdas, clústeres ni métricas. Define el trayecto y el momento; PrediRuta lleva el trabajo analítico a una salida entendible.</p></div>
      <div class="value-grid"><div class="panel value-main"><h3>¿Para quién está pensado?</h3>
        <p>Para quien consulta un desplazamiento en automóvil o motocicleta dentro de Bogotá y quiere revisar el recorrido con más contexto que una ruta y un tiempo estimado.</p>
        <div class="user-row"><span class="chip">Origen</span><span class="chip">Destino</span><span class="chip">Fecha</span><span class="chip">Hora de salida</span></div>
        <div class="output-list"><div class="output"><b>Ruta segmentada</b><span>Google entrega la ruta; PrediRuta la organiza por tramos.</span></div>
          <div class="output"><b>Hora de paso</b><span>Cada tramo se interpreta en el momento previsto.</span></div>
          <div class="output"><b>Clima previsto</b><span>Contexto meteorológico para cada tramo y hora.</span></div></div></div>
        <div class="panel value-impact"><h3>¿Qué valor genera esta consulta?</h3>
          <p>Convierte el recorrido en una lectura por tramos útil para interpretar contexto, patrones y criticidad.</p>
          <div class="value-points">
            <div class="value-point"><b>Integra información dispersa</b><span>Une una ruta, tiempo estimado, accidentalidad histórica y clima previsto.</span></div>
            <div class="value-point"><b>Da contexto por tramo</b><span>Permite leer cada segmento según su momento de paso y su patrón histórico.</span></div>
            <div class="value-point"><b>Apoya análisis preventivos</b><span>Sirve como insumo para revisar puntos críticos y complementar diagnósticos.</span></div>
            <div class="value-point"><b>Hace visible la analítica</b><span>Lleva el trabajo de datos y modelado a una salida clara y consultable.</span></div>
          </div>
          <div class="value-disclaimer">PrediRuta no recomienda rutas; entrega contexto para interpretar el recorrido.</div>
        </div></div>
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
        <figure class="figure"><div class="figure-media"><img src="{imagenes['zonas']}" alt="Distribución de las 150 zonas"></div><figcaption class="figure-caption"><b>Referencia espacial común</b><span>Se definieron 150 zonas tras evaluar la inercia y la distribución de observaciones, buscando un equilibrio entre detalle espacial, concentración de datos y viabilidad computacional.</span></figcaption></figure>
      </div>
    </section>

    <section id="modelos"><div class="section-head"><div class="kicker">Experimentación analítica</div>
      <h2>Modelar fue mucho más que escoger el algoritmo con el número más alto.</h2>
      <p>Se revisaron distribuciones, escenarios de variables, desbalance, hiperparámetros y generalización temporal. Los resultados productivos corresponden a los artefactos exportados en <b>modelo/modelos_produccion</b>.</p></div>
      <div class="model-summary"><div class="model-card"><span class="badge core">Núcleo del MVP</span><h3>Ocurrencia relativa</h3><p>Identifica combinaciones de zona y momento similares a patrones históricos de ocurrencia.</p><div class="decision"><strong>Decisión:</strong> MLP con clima para la señal comparativa.</div></div>
        <div class="model-card"><span class="badge extra">Análisis complementario</span><h3>Estado del actor</h3><p>Evalúa HERIDO, ILESO y MUERTO solo bajo la condición de que ocurriera un siniestro.</p><div class="decision"><strong>Decisión:</strong> XGBoost operativo sin clima.</div></div>
        <div class="model-card"><span class="badge out">Resultado experimental</span><h3>Clase de accidente</h3><p>Se estudió ATROPELLO, CHOQUE y OTROS, pero la señal no respaldó llevarlo al producto.</p><div class="decision"><strong>Decisión:</strong> documentar y no incorporar al MVP.</div></div></div>
      <details class="model-detail" open><summary>Modelo de ocurrencia · señal principal del recorrido</summary><div class="detail-body">
        <div class="detail-copy"><h4>Prioriza combinaciones de lugar y momento</h4><p>Clasifica si en una combinación anual de zona, mes, día y hora se registró al menos un accidente. Es la señal que PrediRuta usa para comparar los tramos del recorrido.</p>
          <div class="method-list">
            <div class="method"><b>Unidad analítica</b><span>5.745.600 combinaciones de año × zona × mes × día × hora.</span></div>
            <div class="method"><b>Diseño temporal</b><span>Entrena 2007–2020, selecciona 2021–2023 y prueba 2024–2025.</span></div>
            <div class="method"><b>Comparación</b><span>Regresión logística, Random Forest, XGBoost y MLP, con y sin clima.</span></div>
            <div class="method"><b>Modelo elegido</b><span>MLP con clima; la mejora frente a la versión sin clima fue pequeña, pero consistente en validación.</span></div>
          </div>
          <div class="metric-line"><span class="metric-pill">ROC-AUC prueba: 0,6308</span><span class="metric-pill">Balanced Accuracy: 0,5981</span><span class="metric-pill">Recall: 69,20 %</span><span class="metric-pill">Precisión: 5,71 %</span><span class="metric-pill">Umbral validado: 0,3090</span></div></div>
        <div class="detail-visuals"><div class="detail-figures"><div class="detail-fig"><img src="{imagenes['ocurrencia']}" alt="Comparación de modelos de ocurrencia"></div><div class="detail-fig"><img src="{imagenes['roc']}" alt="Curva ROC final de ocurrencia"></div></div>
          <p class="model-reading warning"><b>Lectura correcta:</b> es un puntaje comparativo, no la probabilidad de que una persona tenga un accidente. No existe una medida de exposición vehicular y el entrenamiento muestrea negativos para hacer viable el ajuste.</p></div></div></details>
      <details class="model-detail"><summary>Modelo de estado del actor · alcance y desempeño por clase</summary><div class="detail-body">
        <div class="detail-copy"><h4>Una lectura condicional, no un segundo riesgo</h4><p>Estima HERIDO, ILESO o MUERTO bajo el supuesto de que ya ocurrió un siniestro. El diseño operativo excluye datos de la vía y del accidente que no existirían antes de una consulta.</p>
          <div class="method-list">
            <div class="method"><b>Unidad analítica</b><span>1.920.680 actores con estado conocido y tres clases presentes en todos los periodos.</span></div>
            <div class="method"><b>Diseño temporal</b><span>Entrena 2007–2020, selecciona 2021–2023 y prueba 2024–2026.</span></div>
            <div class="method"><b>Modelo elegido</b><span>XGBoost operativo sin clima: 16 entradas disponibles antes del viaje.</span></div>
            <div class="method"><b>Variables que más aportan</b><span>Clase de vehículo; después edad, género y servicio. La zona aporta una señal secundaria.</span></div>
          </div>
          <div class="metric-line"><span class="metric-pill">F1 macro prueba: 0,5688</span><span class="metric-pill">Balanced Accuracy: 0,5926</span><span class="metric-pill">HERIDO F1: 0,831</span><span class="metric-pill">ILESO F1: 0,716</span><span class="metric-pill">MUERTO F1: 0,159</span></div></div>
        <div class="detail-visuals"><div class="detail-figures"><div class="detail-fig"><img src="{imagenes['estado']}" alt="Comparación de modelos de estado"></div><div class="detail-fig"><img src="{imagenes['estado_importancia']}" alt="Importancia de variables del modelo de estado"></div></div>
          <p class="model-reading"><b>Decisión de producto:</b> el clima no mejoró de forma consistente la clasificación operativa. La principal limitación sigue siendo MUERTO: solo cerca del 21 % de esos casos se identifica correctamente.</p></div></div></details>
      <details class="model-detail"><summary>Modelo de clase de accidente · evidencia para no publicarlo</summary><div class="detail-body">
        <div class="detail-copy"><h4>Superó la línea base, pero no el criterio de producto</h4><p>Agrupa los eventos en ATROPELLO, CHOQUE y OTROS. La elevada exactitud aparente se explica por el desbalance: CHOQUE representa cerca del 83 % del histórico.</p>
          <div class="method-list">
            <div class="method"><b>Unidad analítica</b><span>Un accidente; objetivo agrupado en tres clases comparables.</span></div>
            <div class="method"><b>Prueba exigente</b><span>En 2024–2026 CHOQUE baja a 70,43 % y ATROPELLO sube a 20,82 %.</span></div>
            <div class="method"><b>Mejor diseño operativo</b><span>XGBoost sin clima; el aporte meteorológico no fue consistente.</span></div>
            <div class="method"><b>Señal dominante</b><span>La ubicación aporta más que el momento; el clima aporta mucho menos.</span></div>
          </div>
          <div class="metric-line"><span class="metric-pill">F1 macro prueba: 0,3735</span><span class="metric-pill">Balanced Accuracy: 0,3871</span><span class="metric-pill">CHOQUE recall: 79,8 %</span><span class="metric-pill">ATROPELLO recall: 35,3 %</span><span class="metric-pill">OTROS recall: 1,0 %</span></div></div>
        <div class="detail-visuals"><div class="detail-figures"><div class="detail-fig"><img src="{imagenes['clase']}" alt="Comparación de modelos de clase"></div><div class="detail-fig"><img src="{imagenes['clase_matriz']}" alt="Matriz de confusión del modelo de clase"></div></div>
          <p class="model-reading warning"><b>Decisión de producto:</b> no se incorporó al MVP porque el modelo casi no reconoce OTROS y confunde gran parte de ATROPELLO con CHOQUE. Publicarlo habría dado una confianza que la evidencia no respalda.</p></div></div></details>
    </section>

    <section id="producto"><div class="section-head"><div class="kicker">Del notebook a la aplicación</div>
      <h2>PrediRuta separa el flujo que construye el conocimiento del flujo que lo usa en una consulta.</h2>
      <p>El proceso offline prepara, valida y publica artefactos; el flujo online los utiliza para responder una ruta real por tramos.</p></div>
      <div class="flow-system">
        <article class="flow-card">
          <h3>1. Construcción analítica · offline</h3><p>Prepara la base analítica que después se publica para inferencia.</p>
          <div class="flow-items">
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("datos")}</div><div class="flow-copy"><b>Datos fuente</b><span>Accidentalidad histórica + clima histórico.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("ajustes")}</div><div class="flow-copy"><b>Preparación</b><span>Limpieza, relaciones, consistencia y control de calidad.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("espacio")}</div><div class="flow-copy"><b>Transformación espacio–temporal</b><span>Geocodificación, celdas, zonas y variables por hora.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("barras")}</div><div class="flow-copy"><b>Modelado y validación</b><span>Escenarios, métricas, backtesting y análisis de errores.</span></div></div>
          </div>
          <div class="flow-checks"><span class="flow-check"><i>✓</i>Datasets listos</span><span class="flow-check"><i>✓</i>Modelos validados</span><span class="flow-check"><i>✓</i>Metadatos versionados</span></div>
        </article>
        <div class="flow-connector" aria-hidden="true">→</div>
        <article class="flow-card artifacts">
          <h3>2. Artefactos que se publican</h3><p>Son el puente entre los notebooks y la consulta del usuario.</p>
          <div class="flow-items">
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("cubo")}</div><div class="flow-copy"><b>Modelos de inferencia</b><span>Pipelines entrenados y listos para inferencia.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("espacio")}</div><div class="flow-copy"><b>Centroides y zonas</b><span>Capas geoespaciales y partición del territorio.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("documento")}</div><div class="flow-copy"><b>Transformaciones y reglas</b><span>Variables derivadas y reglas de negocio.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("etiqueta")}</div><div class="flow-copy"><b>Metadatos y versiones</b><span>Trazabilidad, versiones y documentación.</span></div></div>
          </div>
          <div class="flow-note"><i>i</i><span>La consulta utiliza modelos entrenados con datos históricos hasta 2023, seleccionados mediante validación temporal y probados sobre los años más recientes.</span></div>
        </article>
        <div class="flow-connector" aria-hidden="true">→</div>
        <article class="flow-card">
          <h3>3. Consulta operativa · online</h3><p>Usa lo publicado para responder una ruta real en el momento de la consulta.</p>
          <div class="flow-items">
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("usuario")}</div><div class="flow-copy"><b>Entrada del usuario</b><span>Origen, destino, fecha y hora.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("ruta")}</div><div class="flow-copy"><b>Google Routes</b><span>Ruta, geometría, duración y tiempos por tramo.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("espacio")}</div><div class="flow-copy"><b>Asignación PrediRuta</b><span>Zona, celda y hora estimada de paso.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("nube")}</div><div class="flow-copy"><b>Contexto</b><span>Clima previsto + lectura histórica por tramo.</span></div></div>
            <div class="flow-item"><div class="flow-item-icon">{_icono_flujo("barras")}</div><div class="flow-copy"><b>Salida</b><span>Mapa por criticidad, tabla por tramos e interpretación.</span></div></div>
          </div>
          <div class="flow-checks"><span class="flow-check"><i>✓</i>Consulta entendible</span><span class="flow-check"><i>✓</i>Sin recomendaciones</span><span class="flow-check"><i>✓</i>Visualización por tramos</span></div>
        </article>
      </div>
      <div class="flow-value">{_icono_flujo("estrella")}<span><b>Valor de producto:</b> separar ambos flujos permite conservar trazabilidad analítica y entregar una consulta clara para el usuario.</span></div>
    </section>

    <section id="limites"><div class="section-head"><div class="kicker">Alcances y límites</div>
      <h2>Las limitaciones también forman parte del proyecto.</h2><p>Hacen explícito cómo debe interpretarse el resultado y qué no puede concluirse.</p></div>
      <div class="limit-grid"><div class="limit"><b>Cobertura</b><span>La versión actual analiza la zona urbana de Bogotá incluida en el entrenamiento.</span></div>
        <div class="limit"><b>Exposición desconocida</b><span>Sin denominador de vehículos expuestos y condiciones de la vía, el score no es una probabilidad individual.</span></div>
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

    <section id="futuro" class="future-section"><div class="section-head"><div class="kicker">Después del MVP actual</div>
      <h2>Una siguiente etapa puede crecer en producto, datos y operación.</h2><p>Estas líneas corresponden a posibles evolutivos del proyecto. El MVP planteado se completó y sus resultados responden a las tablas de requerimientos.</p></div>
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
