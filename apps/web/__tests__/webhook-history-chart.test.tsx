import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookHistoryChart } from "@/components/webhook-history-chart";

describe("WebhookHistoryChart", () => {
  it("renders chart", () => {
    const { container } = render(
      <WebhookHistoryChart period="24h" total={100} success={90} failed={10}
        successRate={90} avgDurationMs={85} byEvent={{ "app.installed": 60, "app.updated": 40 }}
        topEvent="app.installed" />
    );
    expect(container.textContent).toContain("Webhook History");
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("app.installed");
  });
});
