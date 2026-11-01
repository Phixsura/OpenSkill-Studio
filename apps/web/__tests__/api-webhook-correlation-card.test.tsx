import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookCorrelationCard from "../src/components/api-webhook-correlation-card";

const entries = [
  { correlation_id: "c1", event_type: "push", status_code: 200, round_trip_ms: 45.2 },
  { correlation_id: "c2", event_type: "issue", status_code: null, round_trip_ms: null },
];

describe("APIWebhookCorrelationCard", () => {
  it("shows entries", () => {
    const { container } = render(<APIWebhookCorrelationCard entries={entries} pendingCount={1} appName="App" />);
    expect(container.textContent).toContain("Correlations");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("45.2ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookCorrelationCard entries={[]} pendingCount={0} appName="App" />);
    expect(container.textContent).toContain("No correlations");
  });
});
