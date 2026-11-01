import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertDashboard } from "@/components/alert-dashboard";

describe("AlertDashboard", () => {
  it("renders alerts", () => {
    const { container } = render(
      <AlertDashboard active={3} resolved={5} criticalCount={1} status="critical"
        bySeverity={{ critical: 1, warning: 2 }}
        byService={{ api: 2, db: 1 }} />
    );
    expect(container.textContent).toContain("Critical Alerts");
    expect(container.textContent).toContain("3 active");
    expect(container.textContent).toContain("5 resolved");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("api");
  });
});
