import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPlaygroundRunnerCard from "../src/components/api-developer-api-api-playground-runner-card";

const executions = [
  { execution_id: "e1", method: "GET", path: "/api/users", status_code: 200, duration_ms: 45 },
  { execution_id: "e2", method: "POST", path: "/api/users", status_code: 500, duration_ms: 120 },
];

describe("APIDeveloperAPIApiPlaygroundRunnerCard", () => {
  it("shows executions", () => {
    const { container } = render(<APIDeveloperAPIApiPlaygroundRunnerCard executions={executions} avgDuration={82.5} appName="App" />);
    expect(container.textContent).toContain("Playground Runner");
    expect(container.textContent).toContain("avg: 82.5ms");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiPlaygroundRunnerCard executions={[]} avgDuration={0} appName="App" />);
    expect(container.textContent).toContain("No executions");
  });
});
