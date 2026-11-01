import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-gateway-middleware-card";

describe("ConsumerApiGatewayMiddlewareCard", () => {
  it("shows middleware chain", () => {
    const mws = [{ id: "m1", name: "Auth", type: "auth", order: 1, enabled: true }, { id: "m2", name: "Rate Limit", type: "rate_limit", order: 2, enabled: false }];
    const { container } = render(<Card middlewares={mws} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Gateway Middleware");
    expect(container.textContent).toContain("Auth");
    expect(container.textContent).toContain("rate_limit");
    expect(container.textContent).toContain("2 middlewares");
  });
  it("shows empty", () => {
    const { container } = render(<Card middlewares={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No middleware configured");
  });
});
