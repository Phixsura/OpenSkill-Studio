import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogAISummaryCard from "../src/components/changelog-ai-summary-card";

const summary = {
  version: "2.0.0",
  headline: "v2.0.0: 5 changes (1 breaking)",
  bullet_points: [
    "⚠ BREAKING: Removed v1 API",
    "New dashboard (+2 more added)",
    "Fixed login redirect",
  ],
  breaking_count: 1,
  category_counts: { added: 3, fixed: 1, removed: 1 },
  total_changes: 5,
};

describe("ChangelogAISummaryCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogAISummaryCard summary={summary} appName="My App" />);
    expect(container.textContent).toContain("Release Summary");
    expect(container.textContent).toContain("My App");
  });

  it("shows headline", () => {
    const { container } = render(<ChangelogAISummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("v2.0.0: 5 changes");
  });

  it("shows breaking badge", () => {
    const { container } = render(<ChangelogAISummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("1 breaking");
  });

  it("renders category chips", () => {
    const { container } = render(<ChangelogAISummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("added (3)");
    expect(container.textContent).toContain("fixed (1)");
  });

  it("renders bullet points", () => {
    const { container } = render(<ChangelogAISummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("Removed v1 API");
    expect(container.textContent).toContain("New dashboard");
    expect(container.textContent).toContain("Fixed login redirect");
  });

  it("hides breaking badge when zero", () => {
    const noBreaking = { ...summary, breaking_count: 0 };
    const { container } = render(<ChangelogAISummaryCard summary={noBreaking} appName="App" />);
    expect(container.textContent).not.toContain("0 breaking");
  });
});
