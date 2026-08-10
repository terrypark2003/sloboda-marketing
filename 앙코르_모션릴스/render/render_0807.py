#!/usr/bin/env python3
# 8/7(금) 오픈 D-3 인스타 영상 3편
import os, math, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
FONT = "/root/.fonts/NotoSansKR.ttf"
REPO = "/home/user/sloboda-marketing"
OUT = os.path.join(REPO, "앙코르_모션릴스")
TMP = "/tmp/claude-0/-home-user-sloboda-marketing/37ccc5d6-fade-53a4-ab89-8c5618e2d3b1/scratchpad/frames"

W, H, FPS = 1080, 1920, 30

BG    = (244, 239, 230)
CARD  = (255, 255, 255)
INK   = (36, 31, 22)
GREEN = (31, 77, 54)
MINT  = (120, 161, 123)
MUTED = (138, 127, 112)
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
    """0..1 progress of the window [a,b] within local time t"""
    if b <= a: return 1.0 if t >= b else 0.0
    return ease((t - a) / (b - a))

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1], b

def center(d, s, y, f, col, a=1.0, dy=0.0, tracking=0):
    if a <= 0.003: return
    w, h, b = tw(d, s, f)
    x = (W - w) / 2 - b[0]
    d.text((x, y - b[1] + dy), s, font=f, fill=col + (int(255 * min(1.0, a)),))

def left(d, s, x, y, f, col, a=1.0, dy=0.0):
    if a <= 0.003: return
    b = d.textbbox((0, 0), s, font=f)
    d.text((x - b[0], y - b[1] + dy), s, font=f, fill=col + (int(255 * min(1.0, a)),))

def rrect(d, box, r, fill, a=1.0):
    if a <= 0.003: return
    d.rounded_rectangle(box, radius=r, fill=fill + (int(255 * min(1.0, a)),))

def newbg(col=BG):
    im = Image.new("RGB", (W, H), col)
    return im, ImageDraw.Draw(im, "RGBA")

def blend_to(im, col, p):
    if p <= 0.001: return im
    return Image.blend(im, Image.new("RGB", im.size, col), min(1.0, p))


# ─────────────────────────────────────────────────────────
# 릴스 1 — 쿠폰 계산기
# ─────────────────────────────────────────────────────────
def r1_intro(t):
    im, d = newbg()
    center(d, "슬로보다 No.7 리커버리 크림", 250, F(38, 500), MUTED, seg(t, .02, .18))
    a1 = seg(t, .10, .30); a2 = seg(t, .22, .42); a3 = seg(t, .34, .54)
    center(d, "오픈 전에",     760, F(112, 700), INK,   a1, (1 - a1) * 40)
    center(d, "쿠폰부터",      910, F(112, 700), INK,   a2, (1 - a2) * 40)
    center(d, "정리합니다",   1060, F(112, 700), GREEN, a3, (1 - a3) * 40)
    a4 = seg(t, .52, .70)
    rrect(d, (300, 1240, 780, 1330), 45, GREEN, a4 * .10)
    center(d, "8월 10일 (월) 오전 11시", 1285, F(40, 600), GREEN, a4)
    return im


def r1_card(t, label, orig, coupon, cond, final, unit=None):
    im, d = newbg()
    center(d, "슬로보다 No.7 리커버리 크림", 235, F(34, 500), MUTED, seg(t, .0, .12))

    ap = seg(t, .02, .20)
    top, bot = 470, (1470 if unit else 1370)
    cy = int(top + (1 - ap) * 30)
    rrect(d, (86, cy + 10, 994, bot + 10), 42, (222, 214, 200), ap * .55)
    rrect(d, (80, cy,      988, bot),      42, CARD,             ap)

    center(d, label, cy + 105, F(44, 600), MUTED, seg(t, .06, .22))

    # 정가
    ao = seg(t, .10, .26)
    fo = F(104, 700)
    center(d, orig, cy + 250, fo, INK, ao)
    # 취소선
    sp = seg(t, .46, .66)
    if sp > 0:
        wo, ho, bo = tw(d, orig, fo)
        x0 = (W - wo) / 2 - 14
        x1 = x0 + (wo + 28) * sp
        d.line((x0, cy + 262, x1, cy + 262), fill=MUTED + (230,), width=7)

    # 쿠폰 칩
    ac = seg(t, .26, .44)
    if ac > 0.003:
        chip = f"쿠폰  − {coupon}"
        fcp = F(46, 700)
        wc, hc, bc = tw(d, chip, fcp)
        pad, ch = 40, 96
        bx0 = (W - (wc + pad * 2)) / 2 + (1 - ac) * 70
        by = cy + 380
        rrect(d, (bx0, by, bx0 + wc + pad * 2, by + ch), 48, MINT, ac * .22)
        d.text((bx0 + pad - bc[0], by + (ch - hc) / 2 - bc[1]), chip,
               font=fcp, fill=GREEN + (int(255 * ac),))
        center(d, cond, by + ch + 46, F(34, 500), MUTED, seg(t, .32, .48))

    # 최종가
    af = seg(t, .58, .78)
    center(d, final, cy + 660, F(132, 700), GREEN, af, (1 - af) * 34)
    if unit:
        center(d, unit, cy + 848, F(44, 600), MUTED, seg(t, .68, .86))
    return im


def r1_twist(t):
    im, d = newbg()
    center(d, "그런데 하나,", 430, F(58, 500), MUTED, seg(t, .02, .18))
    a1 = seg(t, .12, .32); a2 = seg(t, .24, .44)
    center(d, "1+1 (39,900원)에는",     620, F(84, 700), INK,   a1, (1 - a1) * 34)
    center(d, "기획전 쿠폰이 안 붙습니다", 740, F(84, 700), GREEN, a2, (1 - a2) * 34)

    ab = seg(t, .40, .58)
    rrect(d, (110, 900, 970, 1130), 34, CARD, ab)
    center(d, "와디즈 기획전 쿠폰 3,000원", 985, F(44, 700), INK, seg(t, .44, .60))
    center(d, "5만원 이상 결제 시  →  39,900원은 미달", 1065, F(38, 500), MUTED, seg(t, .50, .66))

    ac = seg(t, .62, .80)
    center(d, "1+1은 저희가 준비한", 1250, F(46, 500), MUTED, ac)
    center(d, "3,000원 쿠폰이 붙는 구성입니다", 1330, F(52, 700), GREEN, seg(t, .68, .86))
    center(d, "쿠폰은 결제 1건에 1장만 적용됩니다", 1500, F(34, 500), MUTED, seg(t, .78, .94))
    return im


def r1_cta(t):
    im, d = newbg()
    a0 = seg(t, .02, .22)
    center(d, "슬로보다 쿠폰 사용기간", 560, F(38, 500), MUTED, a0)
    center(d, "8/10 (월) 11:00 ~ 8/13 (목) 23:59", 640, F(46, 700), INK, seg(t, .08, .28))

    a1 = seg(t, .26, .46)
    rrect(d, (110, 800, 970, 1080), 40, GREEN, a1)
    center(d, "8월 10일 (월) 오전 11시", 900, F(62, 700), WHITE, seg(t, .32, .50))
    center(d, "와디즈 앙코르 오픈", 990, F(44, 500), (215, 232, 219), seg(t, .38, .56))

    a2 = seg(t, .52, .72)
    center(d, "알림신청 해두시면", 1210, F(46, 500), MUTED, a2)
    center(d, "오픈과 동시에 알려드립니다", 1290, F(56, 700), INK, seg(t, .58, .78))
    center(d, "SLOBODA", 1520, F(52, 700), GREEN, seg(t, .74, .92))
    center(d, "슬로보다 No.7 리커버리 크림", 1590, F(32, 400), MUTED, seg(t, .78, .96))
    return im


REEL1 = [
    (96,  r1_intro),
    (120, lambda t: r1_card(t, "슈퍼 얼리버드 · 1개 (선착순 30개)", "24,900원", "2,000원", "2만원 이상 결제 시", "22,900원")),
    (120, lambda t: r1_card(t, "앙코르 단독 1+1 (1차 50세트)",      "39,900원", "3,000원", "3만원 이상 결제 시", "36,900원", "개당 18,450원")),
    (120, lambda t: r1_card(t, "2+1",                                "54,900원", "3,000원", "3만원 이상 결제 시", "51,900원", "개당 17,300원")),
    (115, r1_twist),
    (95,  r1_cta),
]


# ─────────────────────────────────────────────────────────
# 릴스 2 — D-3 실사
# ─────────────────────────────────────────────────────────
def load_cover(path, zoom_from, zoom_to, t, shift=(0.5, 0.5)):
    src = Image.open(path).convert("RGB")
    sw, sh = src.size
    z = zoom_from + (zoom_to - zoom_from) * ease(t)
    tar = W / H
    if sw / sh > tar:
        ch = sh / z; cw = ch * tar
    else:
        cw = sw / z; ch = cw / tar
    cx = shift[0] * sw; cy = shift[1] * sh
    x0 = max(0, min(sw - cw, cx - cw / 2))
    y0 = max(0, min(sh - ch, cy - ch / 2))
    return src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)


def scrim(im, top=0.0, bottom=0.55, col=(20, 17, 12)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for y in range(0, H, 4):
        p = y / H
        a = 0.0
        if p > 1 - bottom:
            a = ((p - (1 - bottom)) / bottom) ** 1.5 * 0.82
        if p < top:
            a = max(a, ((top - p) / top) ** 1.5 * 0.55)
        if a > 0:
            dv.rectangle((0, y, W, y + 4), fill=col + (int(255 * a),))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def r2_s1(t):
    im = load_cover(os.path.join(REPO, "제품컷_신규/p2_podium.png"), 1.00, 1.10, t, (0.5, 0.5))
    im = scrim(im, 0.30, 0.64)
    d = ImageDraw.Draw(im, "RGBA")
    center(d, "와디즈 앙코르", 250, F(40, 500), (235, 228, 216), seg(t, .04, .22))
    a = seg(t, .12, .38)
    center(d, "D-2", 1230, F(200, 700), WHITE, a, (1 - a) * 30)
    center(d, "8월 10일 (월) 오전 11시 오픈", 1420, F(50, 600), (240, 234, 222), seg(t, .30, .52))
    return im


def r2_s2(t):
    im = load_cover(os.path.join(REPO, "제품컷_신규/p5_swatch.png"), 1.14, 1.00, t, (0.5, 0.46))
    im = scrim(im, 0.46, 0.46)
    d = ImageDraw.Draw(im, "RGBA")
    a1 = seg(t, .06, .28); a2 = seg(t, .20, .44)
    center(d, "전성분 첫 줄이",   360, F(86, 700), WHITE, a1, (1 - a1) * 28)
    center(d, "정제수가 아닙니다", 480, F(86, 700), WHITE, a2, (1 - a2) * 28)
    ab = seg(t, .44, .64)
    rrect(d, (90, 1418, 990, 1592), 28, (20, 17, 12), ab * .46)
    center(d, "화장품 전성분은 함량이 많은 순으로 적습니다", 1448, F(36, 600), WHITE, ab)
    center(d, "(1% 이하 성분은 순서 무관)",                 1520, F(32, 400), (222, 216, 204), seg(t, .52, .72))
    return im


def r2_s3(t):
    im, d = newbg()
    center(d, "슬로보다 No.7 리커버리 크림 · 전성분", 250, F(36, 500), MUTED, seg(t, .0, .16))
    rows = [("1", "병풀잎수", GREEN, True), ("2", "판테놀", INK, False), ("3", "정제수", INK, False)]
    y = 520
    for i, (n, name, col, hi) in enumerate(rows):
        a = seg(t, .08 + i * .13, .30 + i * .13)
        if a <= .003:
            y += 230; continue
        if hi:
            rrect(d, (90, y - 70, 990, y + 132), 30, MINT, a * .20)
        left(d, n, 150, y, F(64, 700), MUTED if not hi else GREEN, a)
        left(d, name, 280, y - 12, F(92, 700 if hi else 500), col, a, (1 - a) * 22)
        if hi:
            left(d, "500,000ppm", 280, y + 88, F(40, 600), GREEN, seg(t, .22, .42))
        y += 230
    a4 = seg(t, .58, .78)
    center(d, "정제수는 세 번째입니다", 1400, F(62, 700), INK, a4, (1 - a4) * 26)
    center(d, "※ 500,000ppm은 병풀잎수 기준", 1530, F(32, 400), MUTED, seg(t, .70, .90))
    return im


def r2_s4(t):
    im = load_cover(os.path.join(REPO, "제품컷_신규/p4_travertine.png"), 1.06, 1.16, t, (0.5, 0.52))
    im = scrim(im, 0.52, 0.30)
    d = ImageDraw.Draw(im, "RGBA")
    a1 = seg(t, .06, .28)
    center(d, "8월 10일 (월) 오전 11시", 330, F(66, 700), WHITE, a1, (1 - a1) * 26)
    center(d, "와디즈 앙코르 오픈", 430, F(46, 500), (235, 228, 216), seg(t, .18, .40))
    a2 = seg(t, .34, .56)
    rrect(d, (270, 560, 810, 660), 50, WHITE, a2 * .95)
    center(d, "알림신청 하러 가기", 610, F(44, 700), GREEN, seg(t, .40, .60))
    center(d, "SLOBODA", 1690, F(44, 700), WHITE, seg(t, .58, .80))
    return im


REEL2 = [(105, r2_s1), (105, r2_s2), (120, r2_s3), (105, r2_s4)]


# ─────────────────────────────────────────────────────────
# 스토리 — 하단 770px 비움 (링크 스티커 자리)
# ─────────────────────────────────────────────────────────
def st_1(t):
    """상단 이미지 밴드 + 텍스트. 하단 770px은 링크 스티커 자리로 비움."""
    BAND = 690
    im = Image.new("RGB", (W, H), BG)
    src = Image.open(os.path.join(REPO, "제품컷_신규/p2_podium.png")).convert("RGB")
    sw, sh = src.size
    z = 1.00 + 0.07 * ease(t)
    cw = sw / z
    ch = cw * BAND / W
    cx, cy = sw * 0.5, sh * 0.50
    x0 = max(0, min(sw - cw, cx - cw / 2))
    y0 = max(0, min(sh - ch, cy - ch / 2))
    im.paste(src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
                .resize((W, BAND), Image.LANCZOS), (0, 0))
    # 밴드 하단을 배경색으로 부드럽게 녹임
    ov = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for y in range(150):
        dv.line((0, y, W, y), fill=BG + (int(255 * ease(y / 149)),))
    im.paste(Image.alpha_composite(
        im.crop((0, BAND - 150, W, BAND)).convert("RGBA"), ov).convert("RGB"), (0, BAND - 150))

    d = ImageDraw.Draw(im, "RGBA")
    center(d, "와디즈 앙코르", 735, F(36, 500), MUTED, seg(t, .02, .18))
    a1 = seg(t, .10, .30)
    center(d, "D-3", 800, F(122, 700), GREEN, a1, (1 - a1) * 22)
    a2 = seg(t, .28, .48)
    rrect(d, (130, 950, 950, 1062), 40, GREEN, a2)
    center(d, "8월 10일 (월) 오전 11시", 985, F(52, 700), WHITE, seg(t, .34, .54))
    a3 = seg(t, .50, .68)
    center(d, "쿠폰·구성은 아래에서", 1105, F(38, 500), MUTED, a3)
    bob = math.sin(t * math.pi * 4) * 10
    center(d, "▼", 1165, F(48, 700), MINT, seg(t, .58, .76), bob)
    return im


STORY = [(210, st_1)]


# ─────────────────────────────────────────────────────────
def render(name, scenes, edge_col=None, fade=5):
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


def encode(fdir, out, nframes):
    subprocess.run([
        FF, "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(fdir, "f_%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", out
    ], check=True)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    jobs = [
        ("r2_d2",     REEL2, WHITE, os.path.join(OUT, "0808_릴스2_D2전성분.mp4")),
    ]
    for name, scenes, edge, out in jobs:
        fdir, n = render(name, scenes, edge)
        encode(fdir, out, n)
        sz = os.path.getsize(out) / 1e6
        print(f"OK {os.path.basename(out)}  {n}f  {n/FPS:.1f}s  {sz:.2f}MB")
