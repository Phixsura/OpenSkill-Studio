import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-playground-session-card";

describe("PlaygroundSessionCard", () => {
  it("shows requests", () => {
    const requests = [{ request_id: "r1", method: "GET", path: "/users", response_status: 200, duration_ms: 42 }];
    const { container } = render(<Card sessionId="s1" environment="sandbox" requests={requests} developerName="dev1" appName="App" />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("sandbox");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("200");
  });
  it("shows empty", () => {
    const { container } = render(<Card sessionId="s1" environment="sandbox" requests={[]} developerName="dev1" appName="App" />);
    expect(container.textContent).toContain("No requests yet");
  });
});
