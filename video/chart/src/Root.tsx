import React from "react";
import { Composition } from "remotion";
import { CostRegression } from "./CostRegression";
import { TitleCard, StatPunch, NamedTask, SplitScreen, LogoCta, Explain, Install } from "./Scenes";
import { Captions } from "./Captions";

const base = { fps: 30, width: 1920, height: 1080 } as const;
// Scenes run long (20s) with continuous motion; the assembler trims to the VO
// length — so a held scene is never frozen.
const D = 600;

export const RemotionRoot: React.FC = () => (
  <>
    {/* hero data scene — live UiPath run (README/teaser) */}
    <Composition id="CostRegression" component={CostRegression} durationInFrames={D} {...base} />

    {/* narrated variant for the master at s07 — the 7.27x demo run the VO describes */}
    <Composition id="CostRegression7" component={CostRegression} durationInFrames={D} {...base}
      defaultProps={{
        baseCps: 0.0009, candCps: 0.006543, ratio: 7.27, accDelta: 4.4,
        factors: [
          { name: "model price", mult: 3.0 },
          { name: "verify pass", mult: 2.0 },
          { name: "token volume", mult: 1.21 },
        ],
        kicker: "COSTGUARD — COST-REGRESSION GATE",
        footer: "20 deterministic runs · cost per correctly-processed invoice",
      }} />

    <Composition id="s01-hook" component={TitleCard} durationInFrames={D} {...base}
      defaultProps={{ kicker: "COSTGUARD", line: "It passed the tests. It still cost 7× more." }} />

    <Composition id="s02-gap" component={StatPunch} durationInFrames={D} {...base}
      defaultProps={{ stat: "0", unit: "gates for agent cost", sub: "correctness is tested — cost isn’t" }} />

    <Composition id="s03-name" component={NamedTask} durationInFrames={D} {...base}
      defaultProps={{ label: "The gate", task: "Block this agent version if it costs more per processed invoice" }} />

    {/* NEW — plain-language explanation */}
    <Composition id="s03b-explain" component={Explain} durationInFrames={D} {...base} />

    <Composition id="s06-contrast" component={SplitScreen} durationInFrames={D} {...base}
      defaultProps={{
        leftLabel: "One run", rightLabel: "Twenty runs",
        leftItems: [
          { who: "Quality", text: "looks fine", tone: "ok" },
          { who: "Cost", text: "no signal yet", tone: "muted" },
          { who: "Verdict", text: "would pass", tone: "warn" },
        ],
        rightItems: [
          { who: "Quality", text: "+4.4% accuracy", tone: "ok" },
          { who: "Cost", text: "7.27× per invoice", tone: "accent" },
          { who: "Verdict", text: "FAIL — blocked", tone: "accent" },
        ],
      }} />

    <Composition id="s08-uipath" component={StatPunch} durationInFrames={D} {...base}
      defaultProps={{ stat: "FAIL", unit: "action: block", sub: "real output of an unattended UiPath job (serverless)" }} />

    <Composition id="s10-human" component={TitleCard} durationInFrames={D} {...base}
      defaultProps={{ kicker: "HUMAN IN THE LOOP", line: "Ship it anyway, or quarantine." }} />

    <Composition id="s13-impact" component={StatPunch} durationInFrames={D} {...base}
      defaultProps={{ stat: "7.27×", unit: "cost regression caught", sub: "blocked before production" }} />

    {/* NEW — how to try it */}
    <Composition id="s13b-install" component={Install} durationInFrames={D} {...base} />

    <Composition id="s14-logo" component={LogoCta} durationInFrames={D} {...base}
      defaultProps={{ cta: "github.com/GHGuide/costguard" }} />

    {/* full-timeline caption track — rendered to an alpha mov, overlaid by ffmpeg */}
    <Composition id="Captions" component={Captions} {...base} durationInFrames={300}
      defaultProps={{ events: [], durationInFrames: 300 }}
      calculateMetadata={({ props }) => ({ durationInFrames: props.durationInFrames })} />
  </>
);
