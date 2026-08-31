import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import { ExcludedSection } from "@/components/excluded-section";
import { MatchResultCard, type MatchResultItem } from "@/components/match-result-card";

const result: MatchResultItem = {
  entity_id: "wp1",
  entity_type: "workflow_pack",
  name: "Hero Image Workflow",
  rank: 1,
  score: 0.8734,
  tier: "great",
  reasons: [
    { code: "CAPABILITY_MATCH", label: "Supports image_generation", evidence: "verified" },
    { code: "SCENARIO_MATCH", label: "Matches scenario: ecommerce" },
    { code: "OUTPUT_TYPE_MATCH", label: "Produces image output" },
    { code: "POPULARITY", label: "Widely installed" }, // 4th — must be hidden
  ],
  gaps: [{ code: "MISSING_SKILL", label: "Storyboard skill not yet completed" }],
};

describe("MatchResultCard", () => {
  it("shows the tier label, not the raw score, as visible text (D9/R20)", () => {
    render(<MatchResultCard result={result} />);
    expect(screen.getByText("Excellent match")).toBeDefined();
    // Raw score only in the tooltip (title attr), never as text
    expect(screen.queryByText(/0\.87/)).toBeNull();
    expect(screen.getByTitle(/Score: 0\.8734/)).toBeDefined();
  });

  it("renders at most 3 reason chips", () => {
    render(<MatchResultCard result={result} />);
    expect(screen.getByText("Supports image_generation")).toBeDefined();
    expect(screen.getByText("Matches scenario: ecommerce")).toBeDefined();
    expect(screen.getByText("Produces image output")).toBeDefined();
    expect(screen.queryByText("Widely installed")).toBeNull();
  });

  it("renders gap warnings", () => {
    render(<MatchResultCard result={result} />);
    expect(screen.getByText("Storyboard skill not yet completed")).toBeDefined();
  });

  it("renders remediation link when a href resolver is supplied", () => {
    render(
      <MatchResultCard
        result={result}
        remediationHref={() => "/registry?capability=storyboard"}
      />,
    );
    const link = screen.getByText("Learn this").closest("a");
    expect(link?.getAttribute("href")).toBe("/registry?capability=storyboard");
  });

  it("renders name and rank", () => {
    render(<MatchResultCard result={result} />);
    expect(screen.getByText("Hero Image Workflow")).toBeDefined();
    expect(screen.getByText("#1")).toBeDefined();
  });
});

describe("ExcludedSection", () => {
  it("renders the count and entity names with failure details", () => {
    render(
      <ExcludedSection
        excluded={[
          {
            entity_id: "wp9",
            name: "Audio Pack",
            failures: [
              { code: "CAPABILITY_MISSING", detail: "Pack does not provide capability 'image_generation'" },
            ],
          },
          {
            entity_id: "wp10",
            name: "Video Pack",
            failures: [{ code: "OUTPUT_TYPE_MISMATCH" }],
          },
        ]}
      />,
    );
    expect(screen.getByText("Not eligible (2)")).toBeDefined();
    expect(screen.getByText("Audio Pack")).toBeDefined();
    expect(screen.getByText("Video Pack")).toBeDefined();
    expect(
      screen.getByText("Pack does not provide capability 'image_generation'"),
    ).toBeDefined();
    // Failure without detail falls back to the machine code
    expect(screen.getByText("OUTPUT_TYPE_MISMATCH")).toBeDefined();
  });

  it("renders nothing when the excluded list is empty", () => {
    const { container } = render(<ExcludedSection excluded={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
