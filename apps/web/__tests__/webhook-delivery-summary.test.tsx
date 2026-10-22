import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDeliverySummary } from "@/components/webhook-delivery-summary";

describe("WebhookDeliverySummary", () => {
  it("shows counts", () => {
    const { container } = render(<WebhookDeliverySummary total={100} delivered={90} failed={5} retrying={3} pending={2} successRate={94.7} avgDurationMs={150} />);
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("5");
  });

  it("shows success rate", () => {
    const { container } = render(<WebhookDeliverySummary total={10} delivered={9} failed={1} retrying={0} pending={0} successRate={90.0} avgDurationMs={100} />);
    expect(container.textContent).toContain("90%");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookDeliverySummary total={0} delivered={0} failed={0} retrying={0} pending={0} successRate={100} avgDurationMs={0} />);
    expect(container.textContent).toContain("No webhook");
  });
});
