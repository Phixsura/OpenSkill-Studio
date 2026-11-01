import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PlaygroundRunnerCard from "../src/components/playground-runner-card";

const execs = [
  {
    execution_id: "e1",
    method: "GET",
    path: "/api/users",
    status_code: 200,
    duration_ms: 45,
    saved: true,
    name: "List users",
    timestamp: new Date(Date.now() - 60_000).toISOString(),
  },
  {
    execution_id: "e2",
    method: "POST",
    path: "/api/users",
    status_code: 201,
    duration_ms: 120,
    saved: false,
    name: "",
    timestamp: new Date(Date.now() - 300_000).toISOString(),
  },
  {
    execution_id: "e3",
    method: "DELETE",
    path: "/api/users/1",
    status_code: 404,
    duration_ms: 15,
    saved: false,
    name: "",
    timestamp: new Date(Date.now() - 600_000).toISOString(),
  },
];

describe("PlaygroundRunnerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="My App" />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("My App");
  });

  it("shows request count and saved count", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="App" />);
    expect(container.textContent).toContain("3 requests");
    expect(container.textContent).toContain("1 saved");
  });

  it("renders methods and paths", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("DELETE");
  });

  it("shows status codes", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="App" />);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("404");
  });

  it("shows duration", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="App" />);
    expect(container.textContent).toContain("45ms");
  });

  it("shows saved star", () => {
    const { container } = render(<PlaygroundRunnerCard executions={execs} appName="App" />);
    expect(container.textContent).toContain("⭐");
  });

  it("shows empty state", () => {
    const { container } = render(<PlaygroundRunnerCard executions={[]} appName="App" />);
    expect(container.textContent).toContain("No requests yet");
  });
});
