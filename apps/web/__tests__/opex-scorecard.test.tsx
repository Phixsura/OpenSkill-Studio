import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpexScorecard } from "@/components/opex-scorecard";

describe("OpexScorecard", () => {
  it("renders scorecard", () => {
    const { container } = render(
      <OpexScorecard overall={96} level="elite" doraScore={100} platformScore={90}
        doraBreakdown={{ frequency: 100, lead_time: 100, mttr: 100, change_failure: 100 }} />
    );
    expect(container.textContent).toContain("96");
    expect(container.textContent).toContain("Operational Excellence");
    expect(container.textContent).toContain("elite");
    expect(container.textContent).toContain("DORA Score");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("frequency");
  });
});
