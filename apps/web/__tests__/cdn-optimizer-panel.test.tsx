import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CdnOptimizerPanel } from "@/components/cdn-optimizer-panel";

describe("CdnOptimizerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CdnOptimizerPanel hitRate={75} hits={3000} misses={1000} bandwidthSavedMb={1500}
        regions={[
          { region: "us-east", hitRate: 90, requests: 2000 },
          { region: "eu-west", hitRate: 60, requests: 2000 },
        ]} />
    );
    expect(container.textContent).toContain("CDN Performance");
    expect(container.textContent).toContain("75% hit rate");
    expect(container.textContent).toContain("3,000");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("90%");
  });
});
