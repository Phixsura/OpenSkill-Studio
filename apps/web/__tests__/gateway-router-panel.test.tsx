import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GatewayRouterPanel } from "@/components/gateway-router-panel";

const mockRoutes = [
  { routeId: "r1", method: "GET", pathPattern: "/api/users", extensionId: "ext-1",
    handler: "list_users", middlewares: ["auth", "logging"], authRequired: true,
    rateLimit: 100, priority: 0 },
  { routeId: "r2", method: "POST", pathPattern: "/api/users", extensionId: "ext-1",
    handler: "create_user", middlewares: ["auth"], authRequired: true,
    rateLimit: 0, priority: 0 },
  { routeId: "r3", method: "GET", pathPattern: "/api/health", extensionId: "ext-2",
    handler: "health_check", middlewares: [], authRequired: false,
    rateLimit: 0, priority: 0 },
];

describe("GatewayRouterPanel", () => {
  it("renders routes", () => {
    const { container } = render(<GatewayRouterPanel routes={mockRoutes} />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("list_users");
    expect(container.textContent).toContain("3 routes");
  });

  it("shows middlewares", () => {
    const { container } = render(<GatewayRouterPanel routes={mockRoutes} />);
    expect(container.textContent).toContain("auth → logging");
  });

  it("filters by method", () => {
    const { container } = render(<GatewayRouterPanel routes={mockRoutes} />);
    const btns = container.querySelectorAll("button"); const postBtn = Array.from(btns).find(b => b.textContent === "POST" && b.className.includes("rounded-full")); if (postBtn) fireEvent.click(postBtn);
    expect(container.textContent).toContain("create_user");
    expect(container.textContent).not.toContain("list_users");
  });

  it("calls onTest", () => {
    const onTest = vi.fn();
    const { getAllByText } = render(<GatewayRouterPanel routes={mockRoutes} onTest={onTest} />);
    fireEvent.click(getAllByText("Test")[0]);
    expect(onTest).toHaveBeenCalledWith("GET", "/api/users");
  });
});
