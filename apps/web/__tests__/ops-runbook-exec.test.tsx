import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsRunbookExec } from "@/components/ops-runbook-exec";

describe("OpsRunbookExec", () => {
  it("renders", () => {
    const { container } = render(
      <OpsRunbookExec runbook="restart-service" allOk={true} stepsExecuted={3}
        totalSteps={3} totalDurationMs={1700}
        results={[
          { step: "Stop service", status: "completed", durationMs: 500 },
          { step: "Clear cache", status: "completed", durationMs: 200 },
          { step: "Start service", status: "completed", durationMs: 1000 },
        ]} />
    );
    expect(container.textContent).toContain("restart-service");
    expect(container.textContent).toContain("Complete");
    expect(container.textContent).toContain("3/3");
    expect(container.textContent).toContain("1700ms");
    expect(container.textContent).toContain("Stop service");
    expect(container.textContent).toContain("500ms");
  });
});
