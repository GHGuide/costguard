import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, BG, M, SANS, mono, ramp, rise, breathe, Kicker } from "./theme";

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: BG, fontFamily: SANS, color: C.ink, ...breathe(f) }}>{children}</AbsoluteFill>
  );
};

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

// ---- Explain: what it does, in plain terms — 3 numbered steps (distinct rhythm) ----
export const Explain: React.FC = () => {
  const f = useCurrentFrame();
  const steps = [
    { n: "1", t: "Run the new agent", s: "on the same invoices, many times" },
    { n: "2", t: "Price each correct result", s: "dollars per correctly-done invoice" },
    { n: "3", t: "Block it if it got pricier", s: "same work, higher cost → stop" },
  ];
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 150 }}>
        <Kicker frame={f} text="WHAT COSTGUARD DOES" at={2} />
        <div style={{ fontSize: 62, fontWeight: 700, letterSpacing: -1, marginTop: 16, ...rise(f, 8) }}>
          A spend-checker for your agents
        </div>
      </div>
      {/* connector hairline that draws across the three steps */}
      <div style={{ position: "absolute", left: M + 30, top: 470, width: (1920 - 2 * M - 60) * ramp(f, 24, 70), height: 2, background: C.line }} />
      {steps.map((st, i) => {
        const x = M + i * 540;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 430, width: 470, ...rise(f, 26 + i * 10, 14) }}>
            <div style={{ width: 80, height: 80, borderRadius: 16, border: `2px solid ${C.accent}`, display: "flex", alignItems: "center", justifyContent: "center", background: BG }}>
              <span style={{ ...mono, fontSize: 40, fontWeight: 600, color: C.accent }}>{st.n}</span>
            </div>
            <div style={{ fontSize: 34, fontWeight: 600, marginTop: 28 }}>{st.t}</div>
            <div style={{ fontSize: 24, color: C.body, marginTop: 10, lineHeight: 1.3 }}>{st.s}</div>
          </div>
        );
      })}
    </Frame>
  );
};

// ---- Install: how to try it — a terminal block (different aesthetic on purpose) ----
export const Install: React.FC = () => {
  const f = useCurrentFrame();
  const lines = [
    { at: 24, p: "$", c: "git clone github.com/GHGuide/costguard" },
    { at: 44, p: "$", c: "python3 -m costguard.cli" },
  ];
  const cursorOn = Math.floor(f / 15) % 2 === 0;
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 150 }}>
        <Kicker frame={f} text="TRY IT — TWO COMMANDS" at={2} />
        <div style={{ fontSize: 62, fontWeight: 700, letterSpacing: -1, marginTop: 16, ...rise(f, 8) }}>
          Clone it. Run the gate.
        </div>
      </div>
      {/* terminal panel */}
      <div style={{ position: "absolute", left: M, top: 380, width: 1680, padding: "34px 40px", background: "#0a0e14", border: `1px solid ${C.line}`, borderRadius: 14, ...rise(f, 14, 16) }}>
        <div style={{ ...mono, fontSize: 16, color: C.muted, letterSpacing: 2, marginBottom: 22 }}>costguard — terminal</div>
        {lines.map((ln, i) => (
          <div key={i} style={{ ...mono, fontSize: 30, marginBottom: 18, opacity: ramp(f, ln.at, ln.at + 6) }}>
            <span style={{ color: C.accent, marginRight: 16 }}>{ln.p}</span>
            <span style={{ color: C.ink }}>{ln.c}</span>
            {i === lines.length - 1 && cursorOn ? <span style={{ color: C.accent }}> ▋</span> : null}
          </div>
        ))}
        {/* the verdict it prints */}
        <div style={{ ...mono, fontSize: 28, marginTop: 26, opacity: ramp(f, 70, 80) }}>
          <span style={{ color: C.muted }}>VERDICT  </span>
          <span style={{ color: C.fail, fontWeight: 600 }}>FAIL · block</span>
          <span style={{ color: C.muted }}>   cost/invoice </span>
          <span style={{ color: C.accent }}>7.27×</span>
        </div>
      </div>
      <div style={{ position: "absolute", left: M, top: 760, fontSize: 26, color: C.body, ...rise(f, 88) }}>
        point it at your own agent by editing two lines.
      </div>
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
