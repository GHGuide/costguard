import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, BG, M, SANS, mono, ramp, rise, Kicker } from "./theme";

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: BG, fontFamily: SANS, color: C.ink }}>{children}</AbsoluteFill>
);

// thin accent tick that draws in — the family's recurring mark
const Tick: React.FC<{ frame: number; at?: number; w?: number }> = ({ frame, at = 0, w = 64 }) => (
  <div style={{ width: w * ramp(frame, at, at + 12), height: 4, background: C.accent }} />
);

// ---- TitleCard: kicker + one strong line (s01 hook, s10 human) ----
export const TitleCard: React.FC<{ kicker: string; line: string }> = ({ kicker, line }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 430, width: 1500 }}>
        <Tick frame={f} at={2} />
        <div style={{ marginTop: 26 }}>
          <Kicker frame={f} text={kicker} at={8} />
        </div>
        <div style={{ fontSize: 86, fontWeight: 700, letterSpacing: -1.5, lineHeight: 1.05, marginTop: 18, ...rise(f, 16, 16) }}>
          {line}
        </div>
      </div>
    </Frame>
  );
};

// ---- StatPunch: one dominant figure + unit + sub (s02, s08, s13) ----
export const StatPunch: React.FC<{ stat: string; unit: string; sub: string }> = ({ stat, unit, sub }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 300, width: 1680 }}>
        <Kicker frame={f} text="COSTGUARD" at={2} />
        <div style={{ ...mono, fontSize: 300, fontWeight: 600, lineHeight: 0.86, color: C.accent, marginTop: 16, ...rise(f, 10, 18, 18) }}>
          {stat}
        </div>
        <div style={{ fontSize: 46, fontWeight: 600, marginTop: 20, ...rise(f, 28) }}>{unit}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 26, ...rise(f, 40) }}>
          <div style={{ width: 4, height: 30, background: C.line }} />
          <div style={{ fontSize: 28, color: C.body }}>{sub}</div>
        </div>
      </div>
    </Frame>
  );
};

// ---- NamedTask: a rule/command statement (s03) ----
export const NamedTask: React.FC<{ label: string; task: string }> = ({ label, task }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 388, width: 1500 }}>
        <Kicker frame={f} text={label.toUpperCase()} at={2} />
        <div style={{ display: "flex", gap: 26, marginTop: 28, ...rise(f, 12, 16) }}>
          <div style={{ width: 4, background: C.accent, alignSelf: "stretch" }} />
          <div style={{ ...mono, fontSize: 52, fontWeight: 500, lineHeight: 1.25, color: C.ink }}>{task}</div>
        </div>
      </div>
    </Frame>
  );
};

// ---- SplitScreen: one run vs twenty runs (s06) ----
type Item = { who: string; text: string; tone?: "ok" | "muted" | "warn" | "accent" };
const toneColor = (t?: string) => (t === "accent" ? C.accent : t === "ok" ? C.ok : t === "warn" ? C.body : C.muted);

export const SplitScreen: React.FC<{
  leftLabel: string; rightLabel: string; leftItems: Item[]; rightItems: Item[];
}> = ({ leftLabel, rightLabel, leftItems, rightItems }) => {
  const f = useCurrentFrame();
  const Col: React.FC<{ x: number; label: string; items: Item[]; at: number; dim?: boolean }> = ({ x, label, items, at, dim }) => (
    <div style={{ position: "absolute", left: x, top: 250, width: 640 }}>
      <div style={{ ...mono, fontSize: 20, letterSpacing: 3, color: dim ? C.muted : C.accent, ...rise(f, at) }}>{label.toUpperCase()}</div>
      <div style={{ marginTop: 36 }}>
        {items.map((it, i) => (
          <div key={i} style={{ marginBottom: 30, ...rise(f, at + 6 + i * 4) }}>
            <div style={{ fontSize: 20, color: C.muted, marginBottom: 6 }}>{it.who}</div>
            <div style={{ fontSize: 38, fontWeight: 600, color: toneColor(it.tone) }}>{it.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 120, fontSize: 40, fontWeight: 700, ...rise(f, 2) }}>
        Why run it twenty times?
      </div>
      <Col x={M} label={leftLabel} items={leftItems} at={14} dim />
      <div style={{ position: "absolute", left: 940, top: 250, width: 1, height: 520, background: C.line, opacity: ramp(f, 16, 30) }} />
      <Col x={1040} label={rightLabel} items={rightItems} at={22} />
    </Frame>
  );
};

// ---- LogoCta: wordmark + url (s14) ----
export const LogoCta: React.FC<{ cta: string }> = ({ cta }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 452, width: 1500 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, ...rise(f, 4, 14) }}>
          {/* minimal gate mark */}
          <div style={{ width: 46, height: 46, border: `4px solid ${C.accent}`, borderRadius: 10, position: "relative" }}>
            <div style={{ position: "absolute", left: 8, top: 19, width: 26, height: 4, background: C.accent }} />
          </div>
          <div style={{ fontSize: 76, fontWeight: 700, letterSpacing: -1 }}>CostGuard</div>
        </div>
        <div style={{ fontSize: 32, color: C.body, marginTop: 24, ...rise(f, 16) }}>
          a cost gate for your agents — built and run on UiPath
        </div>
        <div style={{ ...mono, fontSize: 26, color: C.accent, marginTop: 30, ...rise(f, 26) }}>{cta}</div>
      </div>
    </Frame>
  );
};
