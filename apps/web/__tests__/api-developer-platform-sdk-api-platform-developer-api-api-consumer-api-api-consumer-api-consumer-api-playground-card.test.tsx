import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-playground-card";

describe("ConsumerApiPlaygroundCard", () => {
  it("shows history", () => {
    const history = [{ id: "r1", method: "GET", path: "/api/users", status: 200, durationMs: 12.5 }, { id: "r2", method: "POST", path: "/api/orders", status: 201, durationMs: 45 }];
    const { container } = render(<Card history={history} savedCount={3} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("3 saved requests");
  });
  it("shows empty", () => {
    const { container } = render(<Card history={[]} savedCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No recent requests");
  });
});
