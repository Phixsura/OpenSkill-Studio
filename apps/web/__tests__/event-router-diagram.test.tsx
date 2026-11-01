import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventRouterDiagram } from "@/components/event-router-diagram";

describe("EventRouterDiagram", () => {
  it("renders routes", () => {
    const { container } = render(
      <EventRouterDiagram totalRoutes={3} routes={[
        { pattern: "user.*", handler: "user_handler", hits: 150 },
        { pattern: "order.created", handler: "order_handler", hits: 80 },
        { pattern: "#", handler: "audit", hits: 500 },
      ]} />
    );
    expect(container.textContent).toContain("Event Router");
    expect(container.textContent).toContain("3 routes");
    expect(container.textContent).toContain("user.*");
    expect(container.textContent).toContain("user_handler");
    expect(container.textContent).toContain("150 hits");
    expect(container.textContent).toContain("audit");
  });
});
