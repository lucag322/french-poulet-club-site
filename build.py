"""Construit le site publié dans un dossier : copie des fichiers, version suédoise, adresse du site,
robots.txt, sitemap.xml, CNAME et mesure d'audience. Utilisé par les workflows stage et prod.

    python3 build.py --out dist --site https://stage.frenchpouletclub.com --stage
    python3 build.py --out dist --site https://frenchpouletclub.com --cname frenchpouletclub.com --analytics <jeton>
"""
import argparse
import datetime
import pathlib
import re
import shutil

ICI = pathlib.Path(__file__).resolve().parent
FICHIERS = ["index.html", "404.html", "llms.txt", "favicon.svg", "fonts", "img"]

# Traductions de la page anglaise vers le suédois : chaque texte anglais doit exister dans index.html,
# sinon la construction échoue (un texte modifié en anglais doit l'être ici aussi).
SV = [
    ('<html lang="en">', '<html lang="sv">'),
    ("<title>French Poulet Club · French roast chicken in Stockholm</title>",
     "<title>French Poulet Club · Fransk grillad kyckling i Stockholm</title>"),
    ('content="French rotisserie chicken in Stockholm: marinated 24 hours, oven-roasted, served fast. French sides and sauces, no pork. Opening spring 2028."',
     'content="Fransk grillad kyckling i Stockholm: marinerad i 24 timmar, ugnsrostad och snabbt serverad. Franska tillbehör och såser, inget fläsk. Öppnar våren 2028."'),
    ('<link rel="canonical" href="__SITE__/">', '<link rel="canonical" href="__SITE__/sv/">'),
    ('<meta property="og:description" content="French rotisserie chicken in Stockholm. Opening spring 2028.">',
     '<meta property="og:description" content="Fransk grillad kyckling i Stockholm. Öppnar våren 2028.">'),
    ('<meta property="og:url" content="__SITE__/">', '<meta property="og:url" content="__SITE__/sv/">'),
    ('content="French Poulet Club, a roasted chicken leg on a blue background"', 'content="French Poulet Club, ett rostat kycklinglår på blå bakgrund"'),
    ('<meta property="og:locale" content="en_GB">', '<meta property="og:locale" content="sv_SE">'),
    # barre et menu mobile
    ('aria-label="French Poulet Club, back to top"', 'aria-label="French Poulet Club, till toppen"'),
    ('<nav class="liens" aria-label="Main">', '<nav class="liens" aria-label="Huvudmeny">'),
    ('<nav class="panneau" id="panneau" aria-label="Main">', '<nav class="panneau" id="panneau" aria-label="Huvudmeny">'),
    ('    <a href="#menu">Menu</a>\n    <a href="#find-us">Find us</a>\n    <a class="btn" href="#follow">Follow us</a>',
     '    <a href="#menu">Meny</a>\n    <a href="#find-us">Hitta oss</a>\n    <a class="btn" href="#follow">Följ oss</a>'),
    ('<a class="langue" href="sv/" hreflang="sv" lang="sv" aria-label="På svenska">SV</a>',
     '<a class="langue" href="../" hreflang="en" lang="en" aria-label="In English">EN</a>'),
    ('aria-label="Open menu" data-ouvrir="Open menu" data-fermer="Close menu"',
     'aria-label="Öppna menyn" data-ouvrir="Öppna menyn" data-fermer="Stäng menyn"'),
    ('<li><a href="#menu">Menu</a></li>', '<li><a href="#menu">Meny</a></li>'),
    ('<li><a href="#card">Club card</a></li>', '<li><a href="#card">Klubbkort</a></li>'),
    ('<li><a href="#follow">Follow us</a></li>', '<li><a href="#follow">Följ oss</a></li>'),
    ('<li><a href="#find-us">Find us</a></li>', '<li><a href="#find-us">Hitta oss</a></li>'),
    # hero
    ("<b></b>Stockholm · Spring 2028</span>", "<b></b>Stockholm · Våren 2028</span>"),
    ('<a class="btn" href="#menu">See the menu</a>', '<a class="btn" href="#menu">Se menyn</a>'),
    ('<a class="btn creux" href="#follow">Follow us</a>', '<a class="btn creux" href="#follow">Följ oss</a>'),
    ('aria-label="Make the rooster run"', 'aria-label="Få tuppen att springa"'),
    # menu
    ('<h2 class="t" id="t-menu">The menu.</h2>', '<h2 class="t" id="t-menu">Menyn.</h2>'),
    ('<p class="kicker">Prices in kr · VAT included</p>', '<p class="kicker">Priser i kr · inkl. moms</p>'),
    ("<h3><span>Chicken</span><span>Oven roasted · No pork</span></h3>", "<h3><span>Kyckling</span><span>Ugnsrostad · Inget fläsk</span></h3>"),
    ('<span class="nm">3 Drumsticks</span>', '<span class="nm">3 Klubbor</span>'),
    ('<span class="nm">Whole leg<span class="ds">Thigh &amp; drumstick</span>', '<span class="nm">Helt lår<span class="ds">Lår och klubba</span>'),
    ('<span class="nm">Breast<span class="ds">Skin on</span>', '<span class="nm">Bröst<span class="ds">Med skinn</span>'),
    ('<span class="nm">Half chicken</span>', '<span class="nm">Halv kyckling</span>'),
    ('<span class="nm">Whole chicken<span class="ds">To share (or not)</span>', '<span class="nm">Hel kyckling<span class="ds">Att dela (eller inte)</span>'),
    ("<h3><span>Meals</span><span>Chicken + side + sauce</span></h3>", "<h3><span>Måltider</span><span>Kyckling + tillbehör + sås</span></h3>"),
    ('<span class="ds">Any chicken, 1 side, 1 sauce</span>', '<span class="ds">Valfri kyckling, 1 tillbehör, 1 sås</span>'),
    ('<span class="nm">+ Drink</span>', '<span class="nm">+ Dryck</span>'),
    ('<span class="nm">+ Drink + dessert</span>', '<span class="nm">+ Dryck + dessert</span>'),
    ('<span class="ds">With student card</span>', '<span class="ds">Med studentkort</span>'),
    ('<span class="nm">Family<span class="pastille">DEAL</span><span class="ds">Whole chicken, 3 sides, 2 sauces</span>',
     '<span class="nm">Familj<span class="pastille">DEAL</span><span class="ds">Hel kyckling, 3 tillbehör, 2 såser</span>'),
    ("<h3><span>Sides</span><span>39 kr each</span></h3>", "<h3><span>Tillbehör</span><span>39 kr st</span></h3>"),
    ('Pan-fried potatoes <span>/</span> Creamy pasta <span>/</span> Green beans', 'Stekt potatis <span>/</span> Krämig pasta <span>/</span> Gröna bönor'),
    ('<span>Sauces</span><span>12 kr each</span>', '<span>Såser</span><span>12 kr st</span>'),
    ('Green <span>/</span> Onion <span>/</span> Mayo', 'Grön <span>/</span> Lök <span>/</span> Majo'),
    ("<h3><span>More</span></h3>", "<h3><span>Mer</span></h3>"),
    ('<span class="pr soon">Soon</span>', '<span class="pr soon">Snart</span>'),
    ('<span class="nm">Soft drink</span>', '<span class="nm">Läsk</span>'),
    ("<span>Menu and prices may change before opening.</span>", "<span>Meny och priser kan ändras före öppningen.</span>"),
    # carte du club
    ('<p class="kicker" style="color:var(--bleu)">Club card</p>', '<p class="kicker" style="color:var(--bleu)">Klubbkort</p>'),
    ('id="t-fid" style="margin-top:14px">Get<br>stamped.</h2>', 'id="t-fid" style="margin-top:14px">Samla<br>stämplar.</h2>'),
    ("A club card in your phone wallet, scanned at the counter. What it gets you? We'll tell you at the opening.",
     "Ett klubbkort i mobilens plånbok som skannas i kassan. Vad du får? Det berättar vi vid öppningen."),
    ('aria-label="Stamps, tap to fill the card"', 'aria-label="Stämplar, tryck för att fylla kortet"'),
    ('aria-label="Stamp ', 'aria-label="Stämpel '),
    ("<span>Member card</span>", "<span>Medlemskort</span>"),
    ("<span>Card full. See you at the opening.</span>", "<span>Kortet är fullt. Vi ses vid öppningen.</span>"),
    ('<button type="button" id="encore" tabindex="-1">Again</button>', '<button type="button" id="encore" tabindex="-1">Igen</button>'),
    ('data-fin="Voilà ! Card full.">Go on, tap the 6 stamps.</p>', 'data-fin="Voilà ! Kortet är fullt.">Kör, tryck på de 6 stämplarna.</p>'),
    # suivre l'ouverture
    ('id="t-suivre">Be there<br>first.</h2>', 'id="t-suivre">Var där<br>först.</h2>'),
    ("The oven is not on yet. Follow us for the address, the opening day and the first tastings.",
     "Ugnen är inte på än. Följ oss för adressen, öppningsdagen och de första provsmakningarna."),
    # pied de page
    ('<p class="kicker">Stockholm · Opening spring 2028</p>', '<p class="kicker">Stockholm · Öppnar våren 2028</p>'),
    ("French rotisserie chicken in Stockholm. Marinated 24 hours, oven-roasted, served fast, with French sides and sauces. No pork. Exact address soon.",
     "Fransk grillad kyckling i Stockholm. Marinerad i 24 timmar, ugnsrostad och snabbt serverad, med franska tillbehör och såser. Inget fläsk. Exakt adress kommer snart."),
    ("<b>Say hej</b>", "<b>Säg hej</b>"),
]

ANALYTICS = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
             'data-cf-beacon=\'{{"token": "{}"}}\'></script>\n</body>')


def suedois(html):
    for en, sv in SV:
        if en not in html:
            raise SystemExit(f"Traduction introuvable dans index.html : {en[:80]!r}")
        html = html.replace(en, sv)
    # la page suédoise vit dans sv/ : les fichiers du site sont un dossier plus haut
    html = re.sub(r'(?<=[\s"(,])(img|fonts)/', r'../\1/', html)
    return html.replace('href="favicon.svg"', 'href="../favicon.svg"')


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--out", required=True)
    a.add_argument("--site", required=True, help="adresse publique, sans / final")
    a.add_argument("--stage", action="store_true", help="site de test : non indexé")
    a.add_argument("--cname", default="")
    a.add_argument("--analytics", default="", help="jeton Cloudflare Web Analytics")
    o = a.parse_args()
    out, site = pathlib.Path(o.out), o.site.rstrip("/")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in FICHIERS:
        (shutil.copytree if (ICI / f).is_dir() else shutil.copy2)(ICI / f, out / f)
    (out / "sv").mkdir()
    (out / "sv/index.html").write_text(suedois((ICI / "index.html").read_text()))

    pages = [out / "index.html", out / "sv/index.html", out / "404.html"]
    for p in pages + [out / "llms.txt"]:
        t = p.read_text().replace("__SITE__", site)
        if p.suffix == ".html":
            if o.stage:
                t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
            if o.analytics:
                t = t.replace("</body>", ANALYTICS.format(o.analytics), 1)
        p.write_text(t)

    if o.stage:
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    else:
        bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
                "PerplexityBot", "Google-Extended", "Applebot-Extended"]
        (out / "robots.txt").write_text("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\n" for b in bots)
                                        + f"Allow: /\n\nSitemap: {site}/sitemap.xml\n")
        jour = datetime.date.today().isoformat()
        alt = (f'<xhtml:link rel="alternate" hreflang="en" href="{site}/"/>'
               f'<xhtml:link rel="alternate" hreflang="sv" href="{site}/sv/"/>')
        urls = "".join(f"  <url><loc>{site}{u}</loc><lastmod>{jour}</lastmod>{alt}</url>\n" for u in ("/", "/sv/"))
        (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                         'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
    if o.cname:
        (out / "CNAME").write_text(o.cname + "\n")
    print(f"Site construit dans {out} pour {site}" + (" (test, non indexé)" if o.stage else ""))


if __name__ == "__main__":
    main()
