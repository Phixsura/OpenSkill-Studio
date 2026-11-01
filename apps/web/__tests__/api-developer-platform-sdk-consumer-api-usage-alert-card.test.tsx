import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageAlertCard from "../src/components/api-developer-platform-sdk-consumer-api-usage-alert-card";

describe("UsageAlertCard", () => {
  it("renders title and alerts", () => {
    const { container } = render(<UsageAlertCard />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("error_rate");
    expect(container.textContent).toContain("latency_p99");
  });

  it("shows levels and count", () => {
    const { container } = render(<UsageAlertCard />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("3 alerts fired");
  });
});
