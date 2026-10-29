import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookCorrelationTrackerCard from "../src/components/api-developer-api-api-webhook-correlation-tracker-card";

const chains = [
  { correlation_id: "corr-abc", event_count: 3, duration_ms: 1500, event_types: ["push", "build", "deploy"] },
];

describe("APIDeveloperAPIApiWebhookCorrelationTrackerCard", () => {
  it("shows chains", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookCorrelationTrackerCard chains={chains} totalChains={10} appName="App" />);
    expect(container.textContent).toContain("Correlation Tracker");
    expect(container.textContent).toContain("10 chains");
    expect(container.textContent).toContain("corr-abc");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("deploy");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookCorrelationTrackerCard chains={[]} totalChains={0} appName="App" />);
    expect(container.textContent).toContain("No correlation chains");
  });
});
