import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserDashboardLayout } from "@/components/user-dashboard-layout";

describe("UserDashboardLayout", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <UserDashboardLayout greeting="Good day, Alice!" orgName="Acme" plan="pro"
        quickStats={[
          { icon: "📱", value: "5", label: "Apps" },
          { icon: "📡", value: "150,000", label: "API Calls" },
        ]}
        alerts={[{ type: "info", message: "15 notifications" }]}>
        <p>Dashboard content</p>
      </UserDashboardLayout>
    );
    expect(container.textContent).toContain("Good day, Alice!");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("150,000");
    expect(container.textContent).toContain("15 notifications");
    expect(container.textContent).toContain("Dashboard content");
  });
});
