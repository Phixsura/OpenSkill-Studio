import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookSchedulerCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-scheduler-card";

describe("WebhookSchedulerCard", () => {
  it("renders title and schedules", () => {
    const { container } = render(<WebhookSchedulerCard />);
    expect(container.textContent).toContain("Webhook Scheduler");
    expect(container.textContent).toContain("daily_report");
    expect(container.textContent).toContain("health_check");
  });

  it("shows active count", () => {
    const { container } = render(<WebhookSchedulerCard />);
    expect(container.textContent).toContain("2/3 active schedules");
  });
});
