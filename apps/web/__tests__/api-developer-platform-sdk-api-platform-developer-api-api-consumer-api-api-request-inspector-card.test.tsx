import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-inspector-card";

describe("RequestInspectorCard", () => {
  it("shows requests", () => {
    const requests = [{ request_id: "r1", method: "GET", path: "/users", status_code: 200, duration_ms: 42 }];
    const { container } = render(<Card requests={requests} totalInspected={100} appName="App" />);
    expect(container.textContent).toContain("Request Inspector");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("200");
  });
  it("shows empty", () => {
    const { container } = render(<Card requests={[]} totalInspected={0} appName="App" />);
    expect(container.textContent).toContain("No inspected requests");
  });
});
