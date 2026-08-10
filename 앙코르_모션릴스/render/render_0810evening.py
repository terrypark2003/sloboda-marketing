#!/usr/bin/env python3
# 8/10 저녁 2차 세트 — 릴스: 1+1 가격 계산 / 스토리: 쿠폰 리마인드
import os, math
import render_0810b as R
from PIL import Image, ImageDraw

DEEP, DEEP2, CREAM, MINT, FAINT = R.DEEP, R.DEEP2, R.CREAM, R.MINT, R.FAINT
F, seg, center, left, right = R.F, R.seg, R.center, R.left, R.right
rrect, dashline, newdark = R.rrect, R.dashline, R.newdark
tw, ease, grain, dark_base = R.tw, R.ease, R.grain, R.dark_base
W, H = R.W, R.H
OUT = R.OUT
GREEN_INK = (31, 77, 54)


# ── 릴스: 1+1 계산 ───────────────────────────────────────
def e1(t):
    im, d = newdark(51)
    center(d, "와디즈 앙코르 · 1+1 이야기", 340, F(38, 500), MINT, seg(t, .04, .22))
    a1 = seg(t, .14, .38)
    center(d, "두 번째 통은", 600, F(94, 700), CREAM, a1, (1 - a1) * 28)
    center(d, "15,000원입니다", 740, F(94, 700), CREAM, seg(t, .26, .50), (1 - seg(t, .26, .50)) * 28)
    center(d, "첫 통 24,900원 기준", 940, F(38, 500), FAINT, seg(t, .50, .70))
    return im


def e2(t):
    im, d = newdark(52)
    center(d, "1+1 계산서", 240, F(56, 700), CREAM, seg(t, .02, .18))
    rows = [
        ("첫 번째 통",        "24,900원",  CREAM, .06),
        ("두 번째 통",        "15,000원",  CREAM, .16),
        ("1+1 (50mL 2개)",    "39,900원",  MINT,  .28),
        ("쿠폰 · 3만원 이상", "− 3,000원", MINT,  .40),
    ]
    y = 420
    for label, val, col, st in rows:
        a = seg(t, st, st + .16)
        if a > 0.003:
            left(d, label, 140, y, F(40, 500), MINT if col is CREAM else FAINT, a)
            right(d, val, 940, y - 8, F(56, 700), col, a)
            dashline(d, 130, 950, y + 84, FAINT, a)
        y += 130
    a5 = seg(t, .56, .76)
    center(d, "36,900원", 1050, F(112, 700), CREAM, a5, (1 - a5) * 26)
    center(d, "개당 18,450원", 1200, F(48, 600), MINT, seg(t, .66, .84))
    center(d, "쿠폰은 결제 1건에 1장 · 받아두고 결제 때 적용", 1350, F(32, 500), FAINT, seg(t, .76, .92))
    return im


def e3(t):
    im, d = newdark(53)
    a0 = seg(t, .06, .30)
    center(d, "쿠폰은 목요일까지입니다", 620, F(66, 700), CREAM, a0, (1 - a0) * 24)
    a1 = seg(t, .28, .48)
    rrect(d, (200, 800, 880, 910), 55, CREAM, a1 * .97)
    wc, hc, bc = tw(d, "8월 13일(목) 23:59 마감", F(44, 700))
    if a1 > 0.003:
        d.text(((W - wc) / 2 - bc[0], 855 - hc / 2 - bc[1]), "8월 13일(목) 23:59 마감",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .34, .52)),))
    center(d, "2,000원 선착순 30장 · 3,000원 선착순 20장", 1030, F(38, 500), MINT, seg(t, .48, .68))
    return im


def e4(t):
    im, d = newdark(54)
    center(d, "와디즈 앙코르 · 8월 31일(월)까지", 480, F(40, 500), MINT, seg(t, .04, .24))
    a1 = seg(t, .14, .36)
    center(d, "프로필 링크에서", 620, F(78, 700), CREAM, a1, (1 - a1) * 26)
    center(d, "바로 가실 수 있습니다", 740, F(78, 700), CREAM, seg(t, .24, .46), (1 - seg(t, .24, .46)) * 26)
    a2 = seg(t, .46, .64)
    rrect(d, (240, 960, 840, 1070), 55, CREAM, a2 * .97)
    wc, hc, bc = tw(d, "와디즈 앙코르 바로가기", F(44, 700))
    if a2 > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1015 - hc / 2 - bc[1]), "와디즈 앙코르 바로가기",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .52, .70)),))
    dashline(d, 380, 700, 1210, FAINT, seg(t, .60, .76))
    center(d, "SLOBODA", 1300, F(46, 700), CREAM, seg(t, .64, .84))
    return im


REEL = [(95, e1), (135, e2), (85, e3), (90, e4)]


# ── 스토리: 쿠폰 리마인드 (하단 770px 비움) ──────────────
def st(t):
    im = Image.fromarray(grain(dark_base(), 61))
    d = ImageDraw.Draw(im, "RGBA")
    center(d, "오픈 첫날 · 와디즈 앙코르", 700, F(36, 500), MINT, seg(t, .02, .18))
    a1 = seg(t, .10, .30)
    center(d, "쿠폰, 받아두셨나요?", 790, F(88, 700), CREAM, a1, (1 - a1) * 22)
    a2 = seg(t, .28, .48)
    rrect(d, (130, 960, 950, 1072), 40, CREAM, a2)
    wc, hc, bc = tw(d, "2,000원 · 3,000원 ~ 8/13(목)", F(44, 700))
    if a2 > 0.003:
        d.text(((W - wc) / 2 - bc[0], 1016 - hc / 2 - bc[1]), "2,000원 · 3,000원 ~ 8/13(목)",
               font=F(44, 700), fill=GREEN_INK + (int(255 * seg(t, .34, .54)),))
    a3 = seg(t, .50, .68)
    center(d, "링크는 아래에서", 1125, F(38, 500), MINT, a3)
    bob = math.sin(t * math.pi * 4) * 10
    center(d, "▼", 1185, F(48, 700), MINT, seg(t, .58, .76), bob)
    return im


STORY = [(210, st)]


if __name__ == "__main__":
    for name, scenes, edge, out in [
        ("eve_reel",  REEL,  DEEP, os.path.join(OUT, "0810_릴스2_가격계산.mp4")),
        ("eve_story", STORY, None, os.path.join(OUT, "0810_스토리2_쿠폰.mp4")),
    ]:
        fdir, n = R.render(name, scenes, edge)
        R.encode(fdir, out)
        print(f"OK {os.path.basename(out)}  {n}f  {n/30:.1f}s  {os.path.getsize(out)/1e6:.2f}MB")
