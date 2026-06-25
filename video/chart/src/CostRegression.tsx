import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { scaleLinear } from "d3-scale";
import { C, BG, M, SANS, mono, ramp, rise, breathe } from "./theme";

type Factor = { name: string; mult: number };
export type CostProps = {
  baseCps: number;
  candCps: number;
  ratio: number;
  accDelta: number; // percentage points, e.g. 0.0 or 4.4
  factors: Factor[];
  kicker: string;
  footer: string;
};

// default = the live UiPath-gateway run (docs/live-uipath-result.json)
const LIVE: CostProps = {
  baseCps: 0.000133,
  candCps: 0.001742,
  ratio: 13.12,
  accDelta: 0.0,
  factors: [
    { name: "model price", mult: 6.25 },
    { name: "verify pass", mult: 2.0 },
    { name: "token volume", mult: 1.05 },
  ],
  kicker: "COSTGUARD — LIVE ON UIPATH LLM GATEWAY",
  footer: "real models · real tokens · governed by the UiPath AI Trust Layer",
};

export const CostRegression: React.FC<Partial<CostProps>> = (props) => {
  const { baseCps, candCps, ratio, accDelta, factors, kicker, footer } = { ...LIVE, ...props };
  const f = useCurrentFrame();

  const GROUND = 858;
  const H = 520;
  const yScale = scaleLinear().domain([0, candCps]).range([0, H]);
  const maxMult = Math.max(...factors.map((x) => x.mult));

  const candShown = candCps * ramp(f, 22, 94);
  const baseShown = baseCps * ramp(f, 22, 78);
  const ratioShown = ratio * ramp(f, 86, 122);
  const refDraw = ramp(f, 66, 96);
  const underline = ramp(f, 96, 128);
  const hBase = yScale(baseCps);

  const bars = [
    { x: M + 40, cps: baseShown, color: C.base, label: "baseline", sub: "gpt-4.1-mini · simple" },
    { x: M + 220, cps: candShown, color: C.accent, label: "candidate", sub: "gpt-4o · +verify" },
  ];

  return (
    <AbsoluteFill style={{ background: BG, fontFamily: SANS, color: C.ink, ...breathe(f) }}>
      <div style={{ position: "absolute", left: M, top: 92, ...rise(f, 2, 8) }}>
        <div style={{ ...mono, fontSize: 17, letterSpacing: 3, color: C.accent, fontWeight: 600 }}>
          {kicker}
        </div>
      </div>
      <div style={{ position: "absolute", left: M, top: 124, fontSize: 60, fontWeight: 700, letterSpacing: -1, ...rise(f, 6) }}>
        Cost per correctly-processed invoice
      </div>
      <div style={{ position: "absolute", left: M, top: 204, fontSize: 25, color: C.body, ...rise(f, 12) }}>
        baseline vs a “smarter” candidate — 20 runs each, real tokens
      </div>

      {/* axis + 1x reference line */}
      <div style={{ position: "absolute", left: M, top: GROUND, width: 520, height: 1, background: C.line, opacity: ramp(f, 18, 30) }} />
      <div style={{ position: "absolute", left: M, top: GROUND - hBase, width: 520 * refDraw, height: 1, borderTop: `1px dashed ${C.muted}`, opacity: 0.7 }} />
      <div style={{ position: "absolute", left: M + 528, top: GROUND - hBase - 12, ...mono, fontSize: 18, color: C.muted, opacity: refDraw }}>1×</div>

      {bars.map((b, i) => {
        const h = yScale(b.cps);
        return (
          <div key={i} style={{ opacity: ramp(f, 18 + i * 3, 30 + i * 3) }}>
            <div style={{ position: "absolute", left: b.x - 30, top: GROUND - h - 40, width: 160, ...mono, fontSize: 24, color: b.color }}>
              ${b.cps.toFixed(6)}
            </div>
            <div style={{ position: "absolute", left: b.x, top: GROUND - h, width: 80, height: h, background: b.color }} />
            <div style={{ position: "absolute", left: b.x - 30, top: GROUND + 14, width: 160 }}>
              <div style={{ fontSize: 22, fontWeight: 600 }}>{b.label}</div>
              <div style={{ fontSize: 17, color: C.muted, marginTop: 3 }}>{b.sub}</div>
            </div>
          </div>
        );
      })}

      {/* hero figure */}
      <div style={{ position: "absolute", left: 1040, top: 300 }}>
        <div style={{ ...mono, fontSize: 184, fontWeight: 600, lineHeight: 0.9, color: C.accent, ...rise(f, 86, 14, 16) }}>
          {ratioShown.toFixed(2)}×
        </div>
        <div style={{ width: 470 * underline, height: 3, background: C.accent, marginTop: 6 }} />
        <div style={{ fontSize: 33, color: C.ink, marginTop: 22, ...rise(f, 118) }}>
          the cost — for <span style={{ ...mono, color: C.body }}>{accDelta >= 0 ? "+" : ""}{accDelta.toFixed(1)}%</span> accuracy
        </div>
      </div>

      {/* where the cost went */}
      <div style={{ position: "absolute", left: 1040, top: 590, width: 700, ...rise(f, 150) }}>
        <div style={{ ...mono, fontSize: 16, letterSpacing: 3, color: C.muted, marginBottom: 18 }}>WHERE THE COST WENT</div>
        {factors.map((fa, i) => {
          const wRatio = fa.mult / maxMult;
          const w = interpolate(ramp(f, 156 + i * 8, 206 + i * 8), [0, 1], [0, wRatio * 470]);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: 18 }}>
              <div style={{ width: 190, fontSize: 23, color: C.body }}>{fa.name}</div>
              <div style={{ width: 470, height: 8, background: C.hair }}>
                <div style={{ width: w, height: 8, background: C.accent, opacity: 0.45 + 0.55 * wRatio }} />
              </div>
              <div style={{ width: 70, textAlign: "right", ...mono, fontSize: 22, color: C.ink }}>{fa.mult}×</div>
            </div>
          );
        })}
      </div>

      {/* verdict */}
      <div style={{ position: "absolute", left: M, top: 940, display: "flex", alignItems: "center", gap: 20, ...rise(f, 226, 8) }}>
        <div style={{ width: 4, height: 44, background: C.fail }} />
        <div style={{ ...mono, fontSize: 34, fontWeight: 600, color: C.fail, letterSpacing: 1 }}>FAIL</div>
        <div style={{ fontSize: 30, color: C.ink }}>promotion blocked before production</div>
      </div>

      <div style={{ position: "absolute", left: M, top: 1018, ...mono, fontSize: 16, color: C.muted, opacity: ramp(f, 30, 44) }}>
        {footer}
      </div>
      <div style={{ position: "absolute", right: M, top: 1018, ...mono, fontSize: 16, color: C.muted, opacity: ramp(f, 30, 44) }}>
        github.com/GHGuide/costguard
      </div>
    </AbsoluteFill>
  );
};
