import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-mock-server-card";

describe("MockServerCard", () => {
  it("shows mocks", () => {
    const mocks = [{ mock_id: "m1", method: "GET", path: "/users", status_code: 200, hit_count: 42 }];
    const { container } = render(<Card mocks={mocks} totalHits={42} appName="App" />);
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("42 hits");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
  });
  it("shows empty", () => {
    const { container } = render(<Card mocks={[]} totalHits={0} appName="App" />);
    expect(container.textContent).toContain("No mocks defined");
  });
});
