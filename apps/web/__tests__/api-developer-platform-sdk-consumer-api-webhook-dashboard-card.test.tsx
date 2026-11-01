import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookDashboardCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-dashboard-card";

describe("WebhookDashboardCard", () => {
  it("renders title and health counts", () => {
    const { container } = render(<WebhookDashboardCard />);
    expect(container.textContent).toContain("Webhook Dashboard");
    expect(container.textContent).toContain("Healthy");
    expect(container.textContent).toContain("Degraded");
    expect(container.textContent).toContain("Critical");
  });

  it("shows delivery stats", () => {
    const { container } = render(<WebhookDashboardCard />);
    expect(container.textContent).toContain("45,200 deliveries");
    expect(container.textContent).toContain("97.8% success");
  });
});
