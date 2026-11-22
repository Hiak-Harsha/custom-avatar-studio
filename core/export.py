"""
Export Manager
Exports avatar cards, HTML presentation/PDF printable format,
and app icons for embedding anywhere.
"""
import base64
from pathlib import Path


def export_html_card(avatar_path: str, wallpaper_path: str, user_name: str, style_name: str, output_path: str):
    """
    Generates a sleek HTML showcase card that can be viewed in browser,
    printed as PDF, or embedded in web apps.
    """
    with open(avatar_path, "rb") as f:
        avatar_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(wallpaper_path, "rb") as f:
        wall_b64 = base64.b64encode(f.read()).decode("utf-8")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{user_name} - Persona Card ({style_name})</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
  body {{
    background: #0f111a;
    color: #e2e8f0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }}
  .card {{
    background: #1a1d2d;
    border-radius: 1.5rem;
    overflow: hidden;
    max-width: 800px;
    width: 100%;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 30px rgba(0, 242, 254, 0.15);
    border: 1px solid rgba(255,255,255,0.08);
  }}
  .banner {{
    height: 260px;
    background-image: url('data:image/jpeg;base64,{wall_b64}');
    background-size: cover;
    background-position: center;
    position: relative;
  }}
  .banner::after {{
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent 60%, #1a1d2d);
  }}
  .content {{
    padding: 1.5rem 2rem 2.5rem;
    position: relative;
  }}
  .avatar-wrap {{
    position: absolute;
    top: -60px;
    left: 2rem;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid #1a1d2d;
    overflow: hidden;
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    background: #0f111a;
  }}
  .avatar-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .header {{
    margin-left: 140px;
    margin-bottom: 1.5rem;
  }}
  .name {{
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .style-tag {{
    display: inline-block;
    background: rgba(0, 242, 254, 0.12);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.3);
    padding: 0.2rem 0.8rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.3rem;
  }}
  .info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
  }}
  .info-box {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 0.8rem;
    padding: 1rem;
  }}
  .info-title {{
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
  }}
  .info-value {{
    font-size: 1.1rem;
    font-weight: 600;
    color: #f8fafc;
  }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    .card {{ box-shadow: none; border: 1px solid #ccc; }}
  }}
</style>
</head>
<body>
<div class="card">
  <div class="banner"></div>
  <div class="content">
    <div class="avatar-wrap">
      <img src="data:image/jpeg;base64,{avatar_b64}" alt="{user_name}">
    </div>
    <div class="header">
      <div class="name">{user_name}</div>
      <div class="style-tag">Style: {style_name}</div>
    </div>
    <div class="info-grid">
      <div class="info-box">
        <div class="info-title">Persona</div>
        <div class="info-value">Tech Creator & Coder</div>
      </div>
      <div class="info-box">
        <div class="info-title">Terminal Background</div>
        <div class="info-value">Active (CMD / PS)</div>
      </div>
      <div class="info-box">
        <div class="info-title">Desktop Wallpaper</div>
        <div class="info-value">Synchronized</div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    return str(output.resolve())
