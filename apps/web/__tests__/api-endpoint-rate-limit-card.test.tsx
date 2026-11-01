import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointRateLimitCard from "../src/components/api-endpoint-rate-limit-card";

const limits = [{ method: "GET", path: "/api/users", max_rpm: 100, current_count: 85 }];

describe("APIEndpointRateLimitCard", () => {
  it("shows limits", () => {
    const { container } = render(<APIEndpointRateLimitCard limits={limits} appName="App" />);
    expect(container.textContent).toContain("Endpoint Limits");
    expect(container.textContent).toContain("85/100 rpm");
  });
  it("shows empty", () => {
    const { container } = render(<APIEndpointRateLimitCard limits={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoint limits");
  });
});
