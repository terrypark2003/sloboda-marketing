#!/usr/bin/env python3
# 캠페인 주간 릴스 3편 — 딥그린 시스템 유지
# A: 쿠폰 마감(8/13) / B: 이중 임상 0.00 / C: 리뷰
import os, math
import render_0810b as R
from PIL import Image, ImageDraw

DEEP, DEEP2, CREAM, MINT, FAINT = R.DEEP, R.DEEP2, R.CREAM, R.MINT, R.FAINT
F, seg, center, left, right = R.F, R.seg, R.center, R.left, R.right
rrect, dashline, newdark, ticket = R.rrect, R.dashline, R.newdark, R.ticket
tw, ease, grain, dark_base = R.tw, R.ease, R.grain, R.dark_base
W, H = R.W, R.H
REPO, OUT = R.REPO, R.OUT

GREEN_INK = (31, 77, 54)


def star(d, cx, cy, r, col, a, ratio=0.48):
    if a <= 0.003: return
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * ratio
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col + (int(255 * min(1, a)),))


# ══ A. 쿠폰 마감 (8/13 목) ═══════════════════════════════
def a1(t):
    im, d = newdark(21)
    center(d, "와디즈 앙코르", 340, F(38, 500), MINT, seg(t, .04, .22))
    a1_ = seg(t, .14, .38)
    center(d, "쿠폰, 오늘 밤", 620, F(104, 700), CREAM, a1_, (1 - a1_) * 28)
    center(d, "끝납니다", 770, F(104, 700), CREAM, seg(t, .24, .48), (1 - seg(t, .24, .48)) * 28)
    a2_ = seg(t, .48, .68)
    rrect(d, (240, 1000, 840, 1110), 55, CREAM, a2_ * .97)
    wc, hc, bc = tw(d, "8월 13일(목) 23:59 마감", F(44, 700))
    if a2_ > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1055 - hc / 2 - bc[1]), "8월 13일(목) 23:59 마감",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .54, .72)),))
    return im


def a2(t):
    im, d = newdark(22)
    center(d, "아직 안 받으셨다면", 250, F(60, 700), CREAM, seg(t, .02, .20))
    ticket(d, 460, "2,000원", "2만원 이상 결제", "선착순 30장", seg(t, .12, .34))
    ticket(d, 780, "3,000원", "3만원 이상 결제", "선착순 20장", seg(t, .28, .50))
    center(d, "받아두고, 결제 단계에서 적용하세요", 1170, F(44, 600), MINT, seg(t, .52, .72))
    center(d, "쿠폰은 결제 1건에 1장만 적용됩니다", 1280, F(36, 500), FAINT, seg(t, .62, .82))
    return im


def a3(t):
    im, d = newdark(23)
    a0 = seg(t, .04, .26)
    center(d, "쿠폰만 오늘 끝나고,", 560, F(64, 700), CREAM, a0, (1 - a0) * 24)
    center(d, "펀딩은 8월 31일(월)까지", 680, F(64, 700), CREAM, seg(t, .16, .38), (1 - seg(t, .16, .38)) * 24)
    center(d, "계속됩니다", 800, F(64, 700), MINT, seg(t, .28, .50), (1 - seg(t, .28, .50)) * 24)
    a2_ = seg(t, .48, .66)
    rrect(d, (240, 1010, 840, 1120), 55, CREAM, a2_ * .97)
    wc, hc, bc = tw(d, "프로필 링크 → 와디즈", F(44, 700))
    if a2_ > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1065 - hc / 2 - bc[1]), "프로필 링크 → 와디즈",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .54, .72)),))
    center(d, "SLOBODA", 1330, F(46, 700), CREAM, seg(t, .66, .86))
    return im


REEL_A = [(95, a1), (115, a2), (90, a3)]


# ══ B. 이중 임상 0.00 ════════════════════════════════════
def b1(t):
    im = Image.fromarray(grain(dark_base(), 31))
    BAND = 1120
    src = Image.open(os.path.join(REPO, "앙코르_모델컷/model_cand2.png")).convert("RGB")
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
    center(d, "SLOBODA · 임상 이야기", 1170, F(36, 600), MINT, seg(t, .04, .22))
    a1_ = seg(t, .14, .38)
    center(d, "'순하다'는 말 대신,", 1240, F(88, 700), CREAM, a1_, (1 - a1_) * 26)
    center(d, "숫자로 보여드립니다", 1370, F(88, 700), CREAM, seg(t, .28, .52), (1 - seg(t, .28, .52)) * 26)
    return im


def b2(t):
    im, d = newdark(32)
    center(d, "일차자극 인체적용시험", 250, F(54, 700), CREAM, seg(t, .02, .20))
    center(d, "한 번이 아니라, 피부 타입별로 두 번", 350, F(38, 500), MINT, seg(t, .08, .26))
    panels = [((90, 500, 525, 900), "일반 피부", .14), ((555, 500, 990, 900), "민감성 피부", .30)]
    for box, label, st in panels:
        a = seg(t, st, st + .22)
        if a > 0.003:
            rrect(d, box, 30, CREAM, a)
            cxm = (box[0] + box[2]) / 2
            wl, hl, bl = tw(d, label, F(40, 600))
            d.text((cxm - wl / 2 - bl[0], 560 - bl[1]), label, font=F(40, 600),
                   fill=(120, 110, 96, int(255 * a)))
            wz, hz, bz = tw(d, "0.00", F(110, 700))
            d.text((cxm - wz / 2 - bz[0], 680 - bz[1]), "0.00", font=F(110, 700),
                   fill=GREEN_INK + (int(255 * a),))
    a3_ = seg(t, .54, .74)
    center(d, "두 번 시험했고, 두 번 다였습니다", 1020, F(50, 700), CREAM, a3_, (1 - a3_) * 22)
    center(d, "※ 일반·민감성 피부 각각을 대상으로 한 일차자극 인체적용시험 결과", 1220, F(29, 500), FAINT, seg(t, .64, .82))
    center(d, "(보고서번호 HM-IR0089-06 일반 · HM-IR0088-68 민감성)", 1280, F(29, 500), FAINT, seg(t, .68, .86))
    center(d, "※ 모든 사용자에게 자극이 없음을 보증하지 않습니다", 1340, F(29, 500), FAINT, seg(t, .72, .90))
    return im


def b3(t):
    im, d = newdark(33)
    a0 = seg(t, .06, .30)
    center(d, "자극은 시험으로 확인하고,", 640, F(64, 700), CREAM, a0, (1 - a0) * 24)
    center(d, "첫 줄은 병풀잎수로 채웠습니다", 770, F(64, 700), MINT, seg(t, .22, .46), (1 - seg(t, .22, .46)) * 24)
    center(d, "전성분 첫 줄이 정제수가 아닌 크림", 960, F(40, 500), FAINT, seg(t, .46, .66))
    return im


def b4(t):
    im, d = newdark(34)
    center(d, "와디즈 앙코르 · 8월 31일(월)까지", 480, F(40, 500), MINT, seg(t, .04, .24))
    a1_ = seg(t, .14, .36)
    center(d, "숫자는 상세페이지에", 620, F(76, 700), CREAM, a1_, (1 - a1_) * 26)
    center(d, "전부 적어뒀습니다", 740, F(76, 700), CREAM, seg(t, .24, .46), (1 - seg(t, .24, .46)) * 26)
    a2_ = seg(t, .46, .64)
    rrect(d, (240, 950, 840, 1060), 55, CREAM, a2_ * .97)
    wc, hc, bc = tw(d, "프로필 링크 → 와디즈", F(44, 700))
    if a2_ > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1005 - hc / 2 - bc[1]), "프로필 링크 → 와디즈",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .52, .70)),))
    dashline(d, 380, 700, 1200, FAINT, seg(t, .60, .76))
    center(d, "SLOBODA", 1290, F(46, 700), CREAM, seg(t, .64, .84))
    return im


REEL_B = [(100, b1), (135, b2), (90, b3), (95, b4)]


# ══ C. 리뷰 ══════════════════════════════════════════════
def c1(t):
    im, d = newdark(41)
    a0 = seg(t, .06, .30)
    center(d, "광고 말고,", 600, F(90, 700), CREAM, a0, (1 - a0) * 26)
    center(d, "산 분들의 이야기", 740, F(90, 700), CREAM, seg(t, .20, .44), (1 - seg(t, .20, .44)) * 26)
    center(d, "네이버 스마트스토어 구매 리뷰", 950, F(38, 500), MINT, seg(t, .46, .66))
    return im


def c2(t):
    im, d = newdark(42)
    for i in range(5):
        star(d, 300 + i * 120, 560, 52, CREAM, seg(t, .06 + i * .07, .20 + i * .07))
    a1_ = seg(t, .44, .64)
    center(d, "평점 5.0", 700, F(120, 700), CREAM, a1_, (1 - a1_) * 24)
    center(d, "구매 리뷰 61건", 880, F(46, 600), MINT, seg(t, .56, .74))
    center(d, "※ 네이버 스마트스토어 구매 리뷰 · 2026년 7월 기준", 1300, F(30, 500), FAINT, seg(t, .68, .86))
    return im


def c3(t):
    im, d = newdark(43)
    a0 = seg(t, .08, .34)
    center(d, "97%", 520, F(210, 700), CREAM, a0, (1 - a0) * 30)
    center(d, "'촉촉해요'라고 답했습니다", 840, F(56, 700), MINT, seg(t, .30, .52))
    center(d, "※ 네이버 스마트스토어 리뷰 키워드 통계 · 2026년 7월 기준", 1300, F(30, 500), FAINT, seg(t, .54, .74))
    return im


def c4(t):
    im, d = newdark(44)
    a0 = seg(t, .04, .28)
    center(d, "저희는 후기를", 540, F(80, 700), CREAM, a0, (1 - a0) * 26)
    center(d, "만들지 않습니다", 660, F(80, 700), CREAM, seg(t, .16, .40), (1 - seg(t, .16, .40)) * 26)
    center(d, "네이버 구매 리뷰는 구매자만 쓸 수 있습니다", 850, F(38, 500), MINT, seg(t, .40, .60))
    a2_ = seg(t, .52, .70)
    rrect(d, (240, 1010, 840, 1120), 55, CREAM, a2_ * .97)
    wc, hc, bc = tw(d, "프로필 링크 → 와디즈", F(44, 700))
    if a2_ > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1065 - hc / 2 - bc[1]), "프로필 링크 → 와디즈",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .58, .76)),))
    center(d, "SLOBODA", 1330, F(46, 700), CREAM, seg(t, .68, .88))
    return im


REEL_C = [(95, c1), (115, c2), (105, c3), (95, c4)]


if __name__ == "__main__":
    for name, scenes, out in [
        ("wk_a", REEL_A, os.path.join(OUT, "0813_릴스_쿠폰마감.mp4")),
        ("wk_b", REEL_B, os.path.join(OUT, "0815_릴스_이중임상.mp4")),
        ("wk_c", REEL_C, os.path.join(OUT, "0818_릴스_리뷰.mp4")),
    ]:
        fdir, n = R.render(name, scenes, DEEP)
        R.encode(fdir, out)
        print(f"OK {os.path.basename(out)}  {n}f  {n/30:.1f}s  {os.path.getsize(out)/1e6:.2f}MB")
