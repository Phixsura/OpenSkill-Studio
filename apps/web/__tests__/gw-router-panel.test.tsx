import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwRouterPanel } from "@/components/gw-router-panel";
describe("GwRouterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwRouterPanel routes={[
        { pathPrefix: "/api/v1", backend: "api-v1", weight: 100 },
        { pathPrefix: "/api/v2", backend: "api-v2", weight: 50 },
      ]} />
    );
    expect(container.textContent).toContain("Gateway Router");
    expect(container.textContent).toContain("2 routes");
    expect(container.textContent).toContain("/api/v1");
    expect(container.textContent).toContain("api-v1");
    expect(container.textContent).toContain("w:100");
  });
});
