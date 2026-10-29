import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperChangelogAISummaryCard from "../src/components/api-developer-changelog-ai-summary-card";

const summaries = [{ summary_id: "s1", version: "v3.0", summary: "Major release with dark mode", key_points: ["Dark mode", "API v2"] }];

describe("APIDeveloperChangelogAISummaryCard", () => {
  it("shows summaries", () => {
    const { container } = render(<APIDeveloperChangelogAISummaryCard summaries={summaries} appName="App" />);
    expect(container.textContent).toContain("AI Summaries");
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("AI generated");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperChangelogAISummaryCard summaries={[]} appName="App" />);
    expect(container.textContent).toContain("No AI summaries");
  });
});
