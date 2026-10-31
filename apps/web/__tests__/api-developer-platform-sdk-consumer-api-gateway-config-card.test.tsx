import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import GatewayConfigCard from "../src/components/api-developer-platform-sdk-consumer-api-gateway-config-card";

describe("GatewayConfigCard", () => {
  it("renders title and routes", () => {
    const { container } = render(<GatewayConfigCard />);
    expect(container.textContent).toContain("Gateway Config");
    expect(container.textContent).toContain("/api/users/*");
    expect(container.textContent).toContain("/api/orders/*");
  });

  it("shows active count", () => {
    const { container } = render(<GatewayConfigCard />);
    expect(container.textContent).toContain("2/3 routes active");
  });
});
