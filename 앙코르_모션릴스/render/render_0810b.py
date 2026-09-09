#!/usr/bin/env python3
# 8/10 오픈 당일 — 비주얼 리디자인: 모델컷 + 딥그린 다크 그래픽
import os, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
FONT = "/root/.fonts/NotoSansKR.ttf"
REPO = "/home/user/sloboda-marketing"
OUT = os.path.join(REPO, "앙코르_모션릴스")
TMP = "/tmp/claude-0/-home-user-sloboda-marketing/37ccc5d6-fade-53a4-ab89-8c5618e2d3b1/scratchpad/frames"

W, H, FPS = 1080, 1920, 30

DEEP  = (17, 43, 31)     # 딥그린 베이스
DEEP2 = (28, 64, 47)     # 상단 살짝 밝게
CREAM = (243, 238, 228)
MINT  = (156, 196, 166)
FAINT = (104, 138, 116)  # 흐린 보조 텍스트
WHITE = (255, 255, 255)

_fc = {}
def F(size, w=400):
    k = (size, w)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size)
        f.set_variation_by_axes([float(w)])
        _fc[k] = f
    return _fc[k]

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def seg(t, a, b):
    if b <= a: return 1.0 if t >= b else 0.0
    return ease((t - a) / (b - a))

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1], b

def center(d, s, y, f, col, a=1.0, dy=0.0):
    if a <= 0.003: return
    w, h, b = tw(d, s, f)
    d.text(((W - w) / 2 - b[0], y - b[1] + dy), s, font=f, fill=col + (int(255 * min(1, a)),))

def left(d, s, x, y, f, col, a=1.0, dy=0.0):
    if a <= 0.003: return
    b = d.textbbox((0, 0), s, font=f)
    d.text((x - b[0], y - b[1] + dy), s, font=f, fill=col + (int(255 * min(1, a)),))

def right(d, s, x, y, f, col, a=1.0):
    if a <= 0.003: return
    w, h, b = tw(d, s, f)
    d.text((x - w - b[0], y - b[1]), s, font=f, fill=col + (int(255 * min(1, a)),))

def rrect(d, box, r, fill, a=1.0):
    if a <= 0.003: return
    d.rounded_rectangle(box, radius=r, fill=fill + (int(255 * min(1, a)),))

def dashline(d, x0, x1, y, col, a=1.0, dash=22, gap=16, wdt=3):
    if a <= 0.003: return
    x = x0
    while x < x1:
        d.line((x, y, min(x + dash, x1), y), fill=col + (int(255 * min(1, a)),), width=wdt)
        x += dash + gap

# 딥그린 그라데이션 베이스 (1회 계산)
_grad = None
def dark_base():
    global _grad
    if _grad is None:
        col = np.zeros((H, W, 3), dtype=np.float32)
        for y in range(H):
            p = y / (H - 1)
            for c in range(3):
                col[y, :, c] = DEEP2[c] + (DEEP[c] - DEEP2[c]) * min(1.0, p * 1.35)
        # 좌우 가장자리 살짝 어둡게 (비네트)
        xs = np.abs(np.arange(W) - W / 2) / (W / 2)
        vig = 1.0 - 0.10 * (xs ** 2)
        col *= vig[None, :, None]
        _grad = col
    return _grad.copy()

def grain(arr, seed, amp=5):
    rng = np.random.default_rng(seed)
    n = rng.integers(-amp, amp + 1, (H, W, 1)).astype(np.float32)
    return np.clip(arr + n, 0, 255).astype(np.uint8)

def newdark(seed):
    im = Image.fromarray(grain(dark_base(), seed))
    return im, ImageDraw.Draw(im, "RGBA")

def load_cover(path, z0, z1, t, shift=(0.5, 0.5)):
    src = Image.open(path).convert("RGB")
    sw, sh = src.size
    z = z0 + (z1 - z0) * ease(t)
    tar = W / H
    if sw / sh > tar:
        ch = sh / z; cw = ch * tar
    else:
        cw = sw / z; ch = cw / tar
    cx, cy = shift[0] * sw, shift[1] * sh
    x0 = max(0, min(sw - cw, cx - cw / 2))
    y0 = max(0, min(sh - ch, cy - ch / 2))
    return src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def scrim_deep(im, bottom=0.55):
    """하단을 딥그린으로 녹이는 스크림 (검정 대신 브랜드 그린)"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for y in range(0, H, 4):
        p = y / H
        if p > 1 - bottom:
            a = ((p - (1 - bottom)) / bottom) ** 1.4 * 0.94
            dv.rectangle((0, y, W, y + 4), fill=DEEP + (int(255 * a),))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


# ── S1: 모델 밴드 + 딥그린 패널 (겹침 원천 차단) ────────
def s1_model(t):
    im = Image.fromarray(grain(dark_base(), 11))
    BAND = 1120
    src = Image.open(os.path.join(REPO, "앙코르_모델컷/model_cand1.png")).convert("RGB")
    sw, sh = src.size
    z = 1.00 + 0.07 * ease(t)
    cw = sw / z
    ch = cw * BAND / W
    cx, cy = sw * 0.5, sh * 0.40
    x0 = max(0, min(sw - cw, cx - cw / 2))
    y0 = max(0, min(sh - ch, cy - ch / 2))
    im.paste(src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
                .resize((W, BAND), Image.LANCZOS), (0, 0))
    ov = Image.new("RGBA", (W, 180), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for y in range(180):
        dv.line((0, y, W, y), fill=DEEP + (int(255 * ease(y / 179)),))
    im.paste(Image.alpha_composite(
        im.crop((0, BAND - 180, W, BAND)).convert("RGBA"), ov).convert("RGB"), (0, BAND - 180))

    d = ImageDraw.Draw(im, "RGBA")
    center(d, "SLOBODA · 와디즈 앙코르", 1170, F(36, 600), MINT, seg(t, .04, .22))
    a1 = seg(t, .14, .38)
    center(d, "지금, 열렸습니다", 1240, F(96, 700), CREAM, a1, (1 - a1) * 26)
    center(d, "오늘 오전 11시 ~ 8월 31일(월)", 1385, F(40, 500), MINT, seg(t, .34, .56))
    return im


# ── S2: 리워드 — 영수증 스타일 (다크) ────────────────────
def s2_receipt(t, seed):
    im, d = newdark(seed)
    center(d, "오늘 먼저 열리는 것들", 240, F(56, 700), CREAM, seg(t, .02, .20))
    dashline(d, 120, 960, 340, FAINT, seg(t, .08, .24))
    rows = [
        ("슈퍼 얼리버드 · 1개", "24,900원", "선착순 30개"),
        ("앙코르 단독 · 1+1",  "39,900원", "1차 50세트"),
        ("2+1",                "54,900원", "개당 18,300원"),
    ]
    y = 440
    for i, (name, price, note) in enumerate(rows):
        a = seg(t, .10 + i * .14, .32 + i * .14)
        if a > 0.003:
            left(d, name, 130, y, F(38, 500), MINT, a)
            left(d, price, 130, y + 62, F(82, 700), CREAM, a, (1 - a) * 20)
            right(d, note, 950, y + 84, F(38, 600), MINT, a)
            dashline(d, 120, 960, y + 210, FAINT, a)
        y += 300
    a4 = seg(t, .62, .82)
    center(d, "선착순 구성은 소진되면 그대로 닫힙니다", 1390, F(36, 500), FAINT, a4)
    return im


# ── S3: 쿠폰 — 티켓 그래픽 (크림 반전) ───────────────────
def ticket(d, y, amt, cond1, cond2, a):
    if a <= 0.003: return
    x0, x1, hgt = 110, 970, 250
    rrect(d, (x0, y, x1, y + hgt), 30, CREAM, a)
    ymid = y + hgt // 2
    # 펀치 홀 (배경색 원)
    d.ellipse((x0 - 26, ymid - 26, x0 + 26, ymid + 26), fill=DEEP + (int(255 * a),))
    d.ellipse((x1 - 26, ymid - 26, x1 + 26, ymid + 26), fill=DEEP + (int(255 * a),))
    # 절취선
    xd = x0 + 330
    yy = y + 24
    while yy < y + hgt - 24:
        d.line((xd, yy, xd, yy + 14), fill=FAINT + (int(200 * a),), width=3)
        yy += 26
    # 금액
    fa = F(66, 700)
    wc, hc, bc = tw(d, amt, fa)
    d.text(((x0 + xd - wc) / 2 - bc[0], ymid - hc / 2 - bc[1]), amt,
           font=fa, fill=(31, 77, 54, int(255 * a)))
    # 조건
    b1 = d.textbbox((0, 0), cond1, font=F(38, 600))
    d.text((xd + 50 - b1[0], y + 72 - b1[1]), cond1, font=F(38, 600),
           fill=(36, 31, 22, int(255 * a)))
    b2 = d.textbbox((0, 0), cond2, font=F(36, 500))
    d.text((xd + 50 - b2[0], y + 140 - b2[1]), cond2, font=F(36, 500),
           fill=(120, 110, 96, int(255 * a)))

def s3_ticket(t, seed):
    im, d = newdark(seed)
    center(d, "쿠폰 먼저 받으세요", 250, F(60, 700), CREAM, seg(t, .02, .20))
    ticket(d, 460,  "2,000원", "2만원 이상 결제", "선착순 30장", seg(t, .14, .36))
    ticket(d, 780,  "3,000원", "3만원 이상 결제", "선착순 20장", seg(t, .30, .52))
    a3 = seg(t, .52, .72)
    center(d, "8월 13일(목) 23:59까지 · 나흘", 1170, F(50, 700), MINT, a3, (1 - a3) * 22)
    center(d, "쿠폰은 결제 1건에 1장만 적용됩니다", 1285, F(36, 500), FAINT, seg(t, .62, .80))
    center(d, "1+1은 3,000원 쿠폰이 붙는 구성입니다", 1355, F(36, 500), FAINT, seg(t, .70, .88))
    return im


# ── S4: CTA (다크) ───────────────────────────────────────
def s4_cta(t, seed):
    im, d = newdark(seed)
    a0 = seg(t, .04, .24)
    center(d, "와디즈 앙코르 · 8월 31일(월)까지", 420, F(40, 500), MINT, a0)
    a1 = seg(t, .12, .34)
    center(d, "프로필 링크에서", 560, F(80, 700), CREAM, a1, (1 - a1) * 26)
    center(d, "바로 가실 수 있습니다", 680, F(80, 700), CREAM, seg(t, .22, .44), (1 - seg(t, .22, .44)) * 26)
    a2 = seg(t, .42, .62)
    rrect(d, (240, 880, 840, 990), 55, CREAM, a2 * .97)
    wc, hc, bc = tw(d, "와디즈 앙코르 바로가기", F(44, 700))
    if a2 > 0.003:
        d.text(((W - wc) / 2 - bc[0], 935 - hc / 2 - bc[1]), "와디즈 앙코르 바로가기",
               font=F(44, 700), fill=(31, 77, 54, int(255 * seg(t, .48, .66))))
    dashline(d, 380, 700, 1200, FAINT, seg(t, .58, .74))
    center(d, "SLOBODA", 1300, F(48, 700), CREAM, seg(t, .62, .82))
    center(d, "남매 둘이 만드는 브랜드", 1385, F(32, 400), FAINT, seg(t, .70, .88))
    return im


REEL = [
    (100, lambda t: s1_model(t)),
    (125, lambda t, _s=1: s2_receipt(t, _s)),
    (125, lambda t, _s=2: s3_ticket(t, _s)),
    (95,  lambda t, _s=3: s4_cta(t, _s)),
]


# ── 스토리 (다크 · 하단 770px 비움) ──────────────────────
def st_open(t):
    im = Image.fromarray(grain(dark_base(), 77))
    BAND = 660
    src = Image.open(os.path.join(REPO, "앙코르_모델컷/model_cand2.png")).convert("RGB")
    sw, sh = src.size
    z = 1.00 + 0.07 * ease(t)
    cw = sw / z
    ch = cw * BAND / W
    cx, cy = sw * 0.5, sh * 0.30
    x0 = max(0, min(sw - cw, cx - cw / 2))
    y0 = max(0, min(sh - ch, cy - ch / 2))
    band = src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, BAND), Image.LANCZOS)
    im.paste(band, (0, 0))
    # 밴드 하단을 딥그린으로 녹임
    ov = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for y in range(170):
        dv.line((0, y, W, y), fill=DEEP + (int(255 * ease(y / 169)),))
    im.paste(Image.alpha_composite(
        im.crop((0, BAND - 170, W, BAND)).convert("RGBA"), ov).convert("RGB"), (0, BAND - 170))

    d = ImageDraw.Draw(im, "RGBA")
    center(d, "와디즈 앙코르", 715, F(36, 500), MINT, seg(t, .02, .18))
    a1 = seg(t, .10, .30)
    center(d, "열렸습니다", 780, F(108, 700), CREAM, a1, (1 - a1) * 22)
    a2 = seg(t, .28, .48)
    rrect(d, (130, 955, 950, 1067), 40, CREAM, a2)
    wc, hc, bc = tw(d, "쿠폰은 오늘부터 나흘 · ~8/13(목)", F(44, 700))
    if a2 > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1011 - hc / 2 - bc[1]), "쿠폰은 오늘부터 나흘 · ~8/13(목)",
               font=F(44, 700), fill=(31, 77, 54, int(255 * seg(t, .34, .54))))
    a3 = seg(t, .50, .68)
    center(d, "링크는 아래에서", 1115, F(38, 500), MINT, a3)
    bob = math.sin(t * math.pi * 4) * 10
    center(d, "▼", 1175, F(48, 700), MINT, seg(t, .58, .76), bob)
    return im


STORY = [(210, st_open)]


def blend_to(im, col, p):
    if p <= 0.001: return im
    return Image.blend(im, Image.new("RGB", im.size, col), min(1.0, p))

def render(name, scenes, edge_col, fade=5):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    gi = 0
    for n, fn in scenes:
        for i in range(n):
            im = fn(i / max(1, n - 1))
            if edge_col is not None and len(scenes) > 1:
                if i < fade:
                    im = blend_to(im, edge_col, 1 - (i + 1) / fade)
                elif i >= n - fade:
                    im = blend_to(im, edge_col, (i - (n - fade) + 1) / fade)
            im.save(os.path.join(d, f"f_{gi:05d}.png"))
            gi += 1
    return d, gi

def encode(fdir, out):
    subprocess.run([
        FF, "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(fdir, "f_%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", out
    ], check=True)


if __name__ == "__main__":
    for name, scenes, edge, out in [
        ("open_reel_b",  REEL,  DEEP, os.path.join(OUT, "0810_릴스_오픈.mp4")),
        ("open_story_b", STORY, None, os.path.join(OUT, "0810_스토리_오픈.mp4")),
    ]:
        fdir, n = render(name, scenes, edge)
        encode(fdir, out)
        print(f"OK {os.path.basename(out)}  {n}f  {n/FPS:.1f}s  {os.path.getsize(out)/1e6:.2f}MB")
