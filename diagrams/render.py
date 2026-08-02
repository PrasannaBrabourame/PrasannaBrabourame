import cairosvg, sys
STYLE = '''<style>
text{font-family:"DejaVu Sans",sans-serif}
.dl{font-size:12.5px;fill:#14181c}
.ds{font-size:10.5px;fill:#565c63}
.dh{font-family:"DejaVu Serif",serif;font-style:italic;font-size:15px;fill:#1f7a75}
.dc{font-size:11.5px;fill:#8b9198}
.dm{font-family:"DejaVu Sans Mono",monospace;font-size:11px;fill:#8b9198}
.dt{font-size:11.5px;fill:#1f7a75}
.da{font-size:11px;fill:#c9862f}
</style>'''
def png(name, width=1140):
    svg = open(name + ".svg").read()
    svg = svg.replace(">", ">" + STYLE, 1)
    svg = (svg.replace("var(--ink)", "#14181c").replace("var(--teal)", "#1f7a75")
              .replace("var(--amber)", "#c9862f").replace("var(--faint)", "#8b9198"))
    out = "/sessions/happy-keen-tesla/mnt/outputs/dia/%s.png" % name
    cairosvg.svg2png(bytestring=svg.encode(), write_to=out,
                     output_width=width, background_color="#fbfaf7")
    return out
if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(png(n))
