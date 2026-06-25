import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SANS } from "./theme";

export type Ev = { start: number; end: number; text: string };

// A transparent caption track sized to the whole master; rendered to an alpha
// ProRes mov and overlaid by ffmpeg (this ffmpeg build has no text filters).
export const Captions: React.FC<{ events: Ev[]; durationInFrames: number }> = ({ events }) => {
  const f = useCurrentFrame();
  const t = f / 30;
  const cur = events.find((e) => t >= e.start && t < e.end);
  if (!cur) return <AbsoluteFill />;
  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 70, display: "flex", justifyContent: "center" }}>
        <span
          style={{
            maxWidth: 1380,
            fontSize: 40,
            fontWeight: 600,
            color: "#f4f1ec",
            background: "rgba(8,11,15,0.62)",
            padding: "8px 20px",
            borderRadius: 8,
            lineHeight: 1.3,
            textAlign: "center",
            textShadow: "0 1px 3px rgba(0,0,0,0.9)",
          }}
        >
          {cur.text}
        </span>
      </div>
    </AbsoluteFill>
  );
};
