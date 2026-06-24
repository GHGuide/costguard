// Shared design system for every CostGuard scene — one typeface set, one accent,
// one easing. Consistency is the whole point: every shot must look like one hand
// (motion-art-direction). No glow, no emoji, no pills.
import React from "react";
import { interpolate, Easing } from "remotion";
import { loadFont as loadSans } from "@remotion/google-fonts/IBMPlexSans";
import { loadFont as loadMono } from "@remotion/google-fonts/IBMPlexMono";

export const { fontFamily: SANS } = loadSans("normal", { weights: ["400", "500", "600", "700"] });
export const { fontFamily: MONO } = loadMono("normal", { weights: ["500", "600"] });

// 1 accent + tinted neutrals; accent is desaturated + lightened so it never vibrates.
export const C = {
  ink: "#e9edf2",
  body: "#aab2bd",
  muted: "#6b7480",
  line: "#283039",
  hair: "#1c232c",
  base: "#5d6b7a",
  accent: "#e07a42",
  accentDim: "#9a5f43",
  fail: "#cf5b51",
  ok: "#6f9e7e",
};

export const BG = "linear-gradient(176deg, #121821 0%, #0d1219 72%)";
export const M = 120; // outer margin (12-col grid)

// Corporate motion personality: one easing, no overshoot.
export const CORP = Easing.bezier(0.2, 0, 0, 1);
export const ramp = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], { easing: CORP, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
export const rise = (f: number, a: number, dy = 12, len = 14): React.CSSProperties => ({
  opacity: ramp(f, a, a + len),
  transform: `translateY(${interpolate(ramp(f, a, a + len), [0, 1], [dy, 0])}px)`,
});
export const mono: React.CSSProperties = { fontFamily: MONO, fontVariantNumeric: "tabular-nums" };

// A small accent kicker used across scenes — keeps the family identity.
export const Kicker: React.FC<{ frame: number; text: string; at?: number }> = ({ frame, text, at = 2 }) => (
  <div style={{ ...mono, fontSize: 17, letterSpacing: 3, color: C.accent, fontWeight: 600, ...rise(frame, at, 8) }}>
    {text}
  </div>
);
