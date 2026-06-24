import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { scaleLinear } from "d3-scale";

// ---- real numbers (docs/live-uipath-result.json — live on UiPath LLM Gateway) ----
const BASE_CPS = 0.000133;
const CAND_CPS = 0.001742;
const RATIO = 13.12;
const ACC_DELTA = 0.0;
const FACTORS = [
  { name: "model price", mult: 6.25, color: "#ff6a39" },
  { name: "verify pass", mult: 2.0, color: "#f2a93b" },
  { name: "token volume", mult: 1.05, color: "#7c8696" },
];

// ---- palette (UiPath dark) ----
const C = {
  bg0: "#0c1017",
  bg1: "#141b26",
  panel: "#161d28",
  green: "#2ea36a",
  orange: "#fa4616",
  red: "#e5484d",
  text: "#eef1f5",
  muted: "#8b93a1",
  line: "#26303d",
};

const ease = (t: number) => 1 - Math.pow(1 - t, 3);
const prog = (f: number, a: number, b: number) =>
  ease(interpolate(f, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
const fade = (f: number, a: number, len = 12) =>
  interpolate(f, [a, a + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

const tnum: React.CSSProperties = { fontVariantNumeric: "tabular-nums", fontFeatureSettings: '"tnum"' };
const FONT =
  '-apple-system, "Segoe UI", "Helvetica Neue", Inter, Arial, sans-serif';

export const CostRegression: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // bars grow 20->90, easing the VALUE (not just height)
  const grow = prog(frame, 20, 90);
  const baseShown = BASE_CPS * grow;
  const candShown = CAND_CPS * grow;
  const yScale = scaleLinear().domain([0, CAND_CPS]).range([0, 520]);

  // multiplier count-up 78->120
  const ratioShown = RATIO * prog(frame, 78, 120);

  // verdict spring 210->
  const vSpring = spring({ frame: frame - 212, fps, config: { damping: 12, stiffness: 120 } });

  const GROUND = 760; // y of bar baseline
  const barW = 150;

  return (
    <AbsoluteFill style={{ background: `radial-gradient(1200px 700px at 30% 25%, ${C.bg1}, ${C.bg0})`, fontFamily: FONT, color: C.text }}>
      {/* kicker + title */}
      <div style={{ position: "absolute", top: 64, left: 120, opacity: fade(frame, 2) }}>
        <div style={{ color: C.orange, fontSize: 22, fontWeight: 700, letterSpacing: 4 }}>
          COSTGUARD · LIVE ON UIPATH LLM GATEWAY
        </div>
        <div style={{ fontSize: 56, fontWeight: 800, marginTop: 10, letterSpacing: -0.5 }}>
          Cost per correctly-processed invoice
        </div>
      </div>

      {/* ---- the two cost bars ---- */}
      {[
        { x: 360, cps: baseShown, full: BASE_CPS, color: C.green, label: "baseline", sub: "gpt-4.1-mini · simple" },
        { x: 600, cps: candShown, full: CAND_CPS, color: C.orange, label: "candidate", sub: "gpt-4o · + verify" },
      ].map((b, i) => {
        const h = yScale(b.cps);
        return (
          <div key={i} style={{ opacity: fade(frame, 16) }}>
            {/* value label on top of bar */}
            <div style={{ position: "absolute", left: b.x - 20, top: GROUND - h - 52, width: barW + 40, textAlign: "center", fontSize: 30, fontWeight: 700, ...tnum, color: b.color }}>
              ${b.cps.toFixed(6)}
            </div>
            {/* bar */}
            <div style={{ position: "absolute", left: b.x, top: GROUND - h, width: barW, height: h, background: `linear-gradient(180deg, ${b.color}, ${b.color}cc)`, borderRadius: "8px 8px 0 0", boxShadow: `0 0 40px ${b.color}55` }} />
            {/* caption */}
            <div style={{ position: "absolute", left: b.x - 20, top: GROUND + 16, width: barW + 40, textAlign: "center" }}>
              <div style={{ fontSize: 26, fontWeight: 700 }}>{b.label}</div>
              <div style={{ fontSize: 20, color: C.muted, marginTop: 4 }}>{b.sub}</div>
            </div>
          </div>
        );
      })}
      {/* ground line */}
      <div style={{ position: "absolute", left: 300, top: GROUND, width: 560, height: 2, background: C.line, opacity: fade(frame, 16) }} />

      {/* ---- big multiplier ---- */}
      <div style={{ position: "absolute", left: 1040, top: 250, opacity: fade(frame, 80) }}>
        <div style={{ fontSize: 170, fontWeight: 900, lineHeight: 1, color: C.orange, ...tnum, textShadow: `0 0 60px ${C.orange}55` }}>
          {ratioShown.toFixed(2)}×
        </div>
        <div style={{ fontSize: 40, fontWeight: 700, marginTop: 6 }}>more expensive per invoice</div>
        {/* accuracy chip */}
        <div style={{ display: "inline-flex", alignItems: "center", gap: 12, marginTop: 28, padding: "12px 22px", background: C.panel, border: `1px solid ${C.line}`, borderRadius: 999, opacity: fade(frame, 116) }}>
          <span style={{ width: 12, height: 12, borderRadius: 999, background: C.muted }} />
          <span style={{ fontSize: 26, color: C.text }}>accuracy</span>
          <span style={{ fontSize: 26, fontWeight: 800, ...tnum }}>+{ACC_DELTA.toFixed(1)}%</span>
          <span style={{ fontSize: 24, color: C.muted }}>— bought nothing</span>
        </div>
      </div>

      {/* ---- factor breakdown ---- */}
      <div style={{ position: "absolute", left: 1040, top: 600, width: 720, opacity: fade(frame, 142) }}>
        <div style={{ fontSize: 24, color: C.muted, marginBottom: 16, letterSpacing: 2 }}>WHERE THE COST WENT</div>
        {FACTORS.map((f, i) => {
          const w = interpolate(prog(frame, 146 + i * 10, 196 + i * 10), [0, 1], [0, (f.mult / 6.25) * 620]);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
              <div style={{ width: 200, fontSize: 24, color: C.text }}>{f.name}</div>
              <div style={{ width: 620, height: 30, background: "#0e141d", borderRadius: 6, overflow: "hidden" }}>
                <div style={{ width: w, height: 30, background: f.color, borderRadius: 6 }} />
              </div>
              <div style={{ width: 90, textAlign: "right", fontSize: 26, fontWeight: 700, ...tnum, color: f.color }}>{f.mult}×</div>
            </div>
          );
        })}
      </div>

      {/* ---- verdict ---- */}
      <div style={{ position: "absolute", left: 300, top: 880, transform: `scale(${0.6 + 0.4 * vSpring})`, opacity: vSpring, transformOrigin: "left center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 18, padding: "20px 40px", background: `${C.red}1a`, border: `2px solid ${C.red}`, borderRadius: 16 }}>
          <span style={{ fontSize: 46 }}>⛔</span>
          <span style={{ fontSize: 46, fontWeight: 900, color: C.red, letterSpacing: 1 }}>FAIL — promotion blocked</span>
        </div>
      </div>

      {/* footer */}
      <div style={{ position: "absolute", bottom: 40, left: 120, fontSize: 22, color: C.muted, opacity: fade(frame, 30) }}>
        real models · real tokens · governed by the UiPath AI Trust Layer
      </div>
      <div style={{ position: "absolute", bottom: 40, right: 120, fontSize: 22, color: C.muted, opacity: fade(frame, 30) }}>
        github.com/GHGuide/costguard
      </div>
    </AbsoluteFill>
  );
};
