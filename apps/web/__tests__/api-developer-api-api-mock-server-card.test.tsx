import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiMockServerCard from "../src/components/api-developer-api-api-mock-server-card";

const mocks = [
  { endpoint_id: "m1", method: "GET", path: "/api/users", status_code: 200, enabled: true, hit_count: 15, delay_ms: 0 },
  { endpoint_id: "m2", method: "POST", path: "/api/orders", status_code: 201, enabled: false, hit_count: 0, delay_ms: 100 },
];

describe("APIDeveloperAPIApiMockServerCard", () => {
  it("shows mocks", () => {
    const { container } = render(<APIDeveloperAPIApiMockServerCard mocks={mocks} appName="App" />);
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("15 hits");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiMockServerCard mocks={[]} appName="App" />);
    expect(container.textContent).toContain("No mocks configured");
  });
});
