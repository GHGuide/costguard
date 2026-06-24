import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";
import { scaleLinear } from "d3-scale";
import { loadFont as loadSans } from "@remotion/google-fonts/IBMPlexSans";
import { loadFont as loadMono } from "@remotion/google-fonts/IBMPlexMono";

const { fontFamily: SANS } = loadSans("normal", { weights: ["400", "500", "600", "700"] });
const { fontFamily: MONO } = loadMono("normal", { weights: ["500", "600"] });

// ---- real numbers (docs/live-uipath-result.json — live on UiPath LLM Gateway) ----
const BASE_CPS = 0.000133;
const CAND_CPS = 0.001742;
const RATIO = 13.12;
const FACTORS = [
  { name: "model price", mult: 6.25, w: 1.0 },
  { name: "verify pass", mult: 2.0, w: 0.62 },
  { name: "token volume", mult: 1.05, w: 0.34 },
];

// ---- restrained palette: 1 accent + tinted neutrals, no blown-out saturation ----
const C = {
  ink: "#e9edf2",
  body: "#aab2bd",
  muted: "#6b7480",
  line: "#283039",
  hair: "#1c232c",
  base: "#5d6b7a", // baseline data — a quiet slate, not a competing hue
  accent: "#e07a42", // UiPath orange, desaturated + lightened so it doesn't vibrate
  fail: "#cf5b51",
};

// Corporate motion personality: one easing, no overshoot.
const CORP = Easing.bezier(0.2, 0, 0, 1);
const ramp = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], { easing: CORP, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const rise = (f: number, a: number, dy = 10, len = 14): React.CSSProperties => ({
  opacity: ramp(f, a, a + len),
  transform: `translateY(${interpolate(ramp(f, a, a + len), [0, 1], [dy, 0])}px)`,
});
const mono: React.CSSProperties = { fontFamily: MONO, fontVariantNumeric: "tabular-nums" };

export const CostRegression: React.FC = () => {
  const f = useCurrentFrame();

  const M = 120; // outer margin (12-col grid)
  const GROUND = 858;
  const H = 520;
  const yScale = scaleLinear().domain([0, CAND_CPS]).range([0, H]);

  // hero = candidate bar (slowest), support = baseline (a touch quicker)
  const candCps = CAND_CPS * ramp(f, 22, 94);
  const baseCps = BASE_CPS * ramp(f, 22, 78);
  const ratioShown = RATIO * ramp(f, 86, 122);
  const refDraw = ramp(f, 66, 96); // "1x" reference line wipes in
  const underline = ramp(f, 96, 128);

  const bars = [
    { x: M + 40, cps: baseCps, color: C.base, label: "baseline", sub: "gpt-4.1-mini · simple" },
    { x: M + 220, cps: candCps, color: C.accent, label: "candidate", sub: "gpt-4o · +verify" },
  ];
  const hBase = yScale(BASE_CPS);

  return (
    <AbsoluteFill style={{ background: "linear-gradient(176deg, #121821 0%, #0d1219 70%)", fontFamily: SANS, color: C.ink }}>
      {/* ---- header (top-left, editorial) ---- */}
      <div style={{ position: "absolute", left: M, top: 92, ...rise(f, 2) }}>
        <div style={{ ...mono, fontSize: 17, letterSpacing: 3, color: C.accent, fontWeight: 600 }}>
          COSTGUARD — LIVE ON UIPATH LLM GATEWAY
        </div>
      </div>
      <div style={{ position: "absolute", left: M, top: 124, fontSize: 60, fontWeight: 700, letterSpacing: -1, ...rise(f, 6) }}>
        Cost per correctly-processed invoice
      </div>
      <div style={{ position: "absolute", left: M, top: 204, fontSize: 25, color: C.body, ...rise(f, 12) }}>
        baseline vs a “smarter” candidate — 20 runs each, real tokens
      </div>

      {/* ---- bars (lower-left) ---- */}
      {/* axis baseline */}
      <div style={{ position: "absolute", left: M, top: GROUND, width: 520, height: 1, background: C.line, opacity: ramp(f, 18, 30) }} />
      {/* 1x reference line at baseline height */}
      <div style={{ position: "absolute", left: M, top: GROUND - hBase, width: 520 * refDraw, height: 1, borderTop: `1px dashed ${C.muted}`, opacity: 0.7 }} />
      <div style={{ position: "absolute", left: M + 528, top: GROUND - hBase - 12, ...mono, fontSize: 18, color: C.muted, opacity: refDraw }}>1×</div>

      {bars.map((b, i) => {
        const h = yScale(b.cps);
        return (
          <div key={i} style={{ opacity: ramp(f, 18 + i * 3, 30 + i * 3) }}>
            <div style={{ position: "absolute", left: b.x - 30, top: GROUND - h - 40, width: 140, ...mono, fontSize: 24, color: b.color }}>
              ${b.cps.toFixed(6)}
            </div>
            <div style={{ position: "absolute", left: b.x, top: GROUND - h, width: 80, height: h, background: b.color }} />
            <div style={{ position: "absolute", left: b.x - 30, top: GROUND + 14, width: 140 }}>
              <div style={{ fontSize: 22, fontWeight: 600 }}>{b.label}</div>
              <div style={{ fontSize: 17, color: C.muted, marginTop: 3 }}>{b.sub}</div>
            </div>
          </div>
        );
      })}

      {/* ---- hero figure (right third, off-center) ---- */}
      <div style={{ position: "absolute", left: 1040, top: 300 }}>
        <div style={{ ...mono, fontSize: 184, fontWeight: 600, lineHeight: 0.9, color: C.accent, ...rise(f, 86, 14, 16) }}>
          {ratioShown.toFixed(2)}×
        </div>
        <div style={{ width: 470 * underline, height: 3, background: C.accent, marginTop: 6 }} />
        <div style={{ fontSize: 33, color: C.ink, marginTop: 22, ...rise(f, 118) }}>
          the cost — for <span style={{ ...mono, color: C.body }}>+0.0%</span> accuracy
        </div>
      </div>

      {/* ---- where the cost went ---- */}
      <div style={{ position: "absolute", left: 1040, top: 590, width: 700, ...rise(f, 150) }}>
        <div style={{ ...mono, fontSize: 16, letterSpacing: 3, color: C.muted, marginBottom: 18 }}>WHERE THE COST WENT</div>
        {FACTORS.map((fa, i) => {
          const w = interpolate(ramp(f, 156 + i * 8, 206 + i * 8), [0, 1], [0, fa.w * 470]);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: 18 }}>
              <div style={{ width: 190, fontSize: 23, color: C.body }}>{fa.name}</div>
              <div style={{ width: 470, height: 8, background: C.hair }}>
                <div style={{ width: w, height: 8, background: C.accent, opacity: 0.45 + 0.55 * fa.w }} />
              </div>
              <div style={{ width: 70, textAlign: "right", ...mono, fontSize: 22, color: C.ink }}>{fa.mult}×</div>
            </div>
          );
        })}
      </div>

      {/* ---- verdict (lower-left, no pill / no emoji) ---- */}
      <div style={{ position: "absolute", left: M, top: 940, display: "flex", alignItems: "center", gap: 20, ...rise(f, 226, 8) }}>
        <div style={{ width: 4, height: 44, background: C.fail }} />
        <div style={{ ...mono, fontSize: 34, fontWeight: 600, color: C.fail, letterSpacing: 1 }}>FAIL</div>
        <div style={{ fontSize: 30, color: C.ink }}>promotion blocked before production</div>
      </div>

      {/* ---- footers ---- */}
      <div style={{ position: "absolute", left: M, top: 1018, ...mono, fontSize: 16, color: C.muted, opacity: ramp(f, 30, 44) }}>
        real models · real tokens · governed by the UiPath AI Trust Layer
      </div>
      <div style={{ position: "absolute", right: M, top: 1018, ...mono, fontSize: 16, color: C.muted, opacity: ramp(f, 30, 44) }}>
        github.com/GHGuide/costguard
      </div>
    </AbsoluteFill>
  );
};
