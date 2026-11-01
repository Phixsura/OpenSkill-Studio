import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DevConsoleDashboard } from "@/components/dev-console-dashboard";

describe("DevConsoleDashboard", () => {
  it("renders dashboard", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <DevConsoleDashboard devName="Acme" plan="pro" verified={true}
        totalApps={5} installsDisplay="8,000" avgRating={4.3}
        apiDisplay="150,000" openIssues={3}
        recentDeploys={[{ app: "App1", version: "2.1", status: "success", time: "5m ago" }]}
        quickActions={[{ label: "Create App", icon: "📱", action: "create_app" }]}
        onAction={onAction} />
    );
    expect(container.textContent).toContain("Welcome back, Acme");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("150,000");
    expect(container.textContent).toContain("App1 v2.1");
    fireEvent.click(getByText("Create App"));
    expect(onAction).toHaveBeenCalledWith("create_app");
  });
});
