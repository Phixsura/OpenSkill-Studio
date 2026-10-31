import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-api-consumer-api-playground-v2-card";

describe("ApiPlaygroundV2Card", () => {
  it("shows collections and history", () => {
    const collections = [{ id: "c1", name: "Auth Tests", requests: [{ id: "r1", name: "Login", method: "POST", path: "/api/auth" }] }];
    const history = [{ requestId: "r1", status: 200, latencyMs: 15, executedAt: "12:00" }];
    const { container } = render(<Card collections={collections} history={history} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Playground V2");
    expect(container.textContent).toContain("Auth Tests");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("200");
  });
  it("shows empty", () => {
    const { container } = render(<Card collections={[]} history={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Start exploring");
  });
});
