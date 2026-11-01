import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployTimelineView } from "@/components/deploy-timeline-view";

describe("DeployTimelineView", () => {
  it("renders", () => {
    const { container } = render(
      <DeployTimelineView total={10} successRate={90} avgDurationSec={120}
        byEnvironment={{ production: 5, staging: 5 }}
        deploys={[
          { environment: "production", status: "success", version: "3.0" },
          { environment: "staging", status: "failed", version: "3.1" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Timeline");
    expect(container.textContent).toContain("10 deploys");
    expect(container.textContent).toContain("90% success");
    expect(container.textContent).toContain("production: 5");
    expect(container.textContent).toContain("v3.0");
  });
});
