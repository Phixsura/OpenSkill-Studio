import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlowEpPanel } from "@/components/slow-ep-panel";
describe("SlowEpPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SlowEpPanel totalEndpoints={5} thresholdMs={200}
        slowEndpoints={[{ endpoint: "/slow", avgMs: 150, p99Ms: 500, samples: 100 }]} />
    );
    expect(container.textContent).toContain("Slow Endpoints");
    expect(container.textContent).toContain("1/5 slow");
    expect(container.textContent).toContain("/slow");
    expect(container.textContent).toContain("p99 500ms");
  });
});
