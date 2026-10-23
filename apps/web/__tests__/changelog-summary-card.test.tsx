import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogSummaryCard } from "@/components/changelog-summary-card";

describe("ChangelogSummaryCard", () => {
  it("renders summary", () => {
    const { container } = render(
      <ChangelogSummaryCard version="3.0.0" summary="v3.0.0: 2 features, 1 fix"
        totalChanges={4} typeCounts={{ added: 2, fixed: 1, breaking: 1 }}
        highlights={["Dark mode"]} hasBreaking={true} contributorCount={2} />
    );
    expect(container.textContent).toContain("v3.0.0");
    expect(container.textContent).toContain("2 features");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("2 contributors");
  });
});
