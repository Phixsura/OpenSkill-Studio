import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-health-score-card";

describe("EndpointHealthScoreCard", () => {
  it("shows scores", () => {
    const scores = [{ path: "/api/users", score: 95.2, grade: "A", status: "healthy", uptimeScore: 100, latencyScore: 97.5, errorScore: 99 }];
    const { container } = render(<Card scores={scores} appName="App" />);
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("95.2");
  });
  it("shows empty", () => {
    const { container } = render(<Card scores={[]} appName="App" />);
    expect(container.textContent).toContain("No health data");
  });
});
