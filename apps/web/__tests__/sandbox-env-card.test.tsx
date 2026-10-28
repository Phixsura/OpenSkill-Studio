import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SandboxEnvCard from "../src/components/sandbox-env-card";

const runningSandbox = {
  sandbox_id: "sb-abc123",
  app_version: "2.1.0",
  status: "running" as const,
  memory_limit_mb: 256,
  memory_used_mb: 128,
  cpu_used_seconds: 12.5,
  created_at: new Date(Date.now() - 600_000).toISOString(),
  exit_code: null,
  log_lines: 42,
};

const stoppedSandbox = {
  sandbox_id: "sb-def456",
  app_version: "2.0.0",
  status: "stopped" as const,
  memory_limit_mb: 512,
  memory_used_mb: 0,
  cpu_used_seconds: 85.3,
  created_at: new Date(Date.now() - 3_600_000).toISOString(),
  exit_code: 0,
  log_lines: 200,
};

const terminatedSandbox = {
  sandbox_id: "sb-ghi789",
  app_version: "1.9.0",
  status: "terminated" as const,
  memory_limit_mb: 256,
  memory_used_mb: 245,
  cpu_used_seconds: 300,
  created_at: new Date(Date.now() - 7_200_000).toISOString(),
  exit_code: 137,
  log_lines: 500,
};

describe("SandboxEnvCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[runningSandbox]} appName="My App" />);
    expect(container.textContent).toContain("Sandboxes");
    expect(container.textContent).toContain("My App");
  });

  it("shows running count", () => {
    const { container } = render(
      <SandboxEnvCard sandboxes={[runningSandbox, stoppedSandbox]} appName="App" />,
    );
    expect(container.textContent).toContain("1 running");
  });

  it("renders sandbox id and version", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[runningSandbox]} appName="App" />);
    expect(container.textContent).toContain("sb-abc123");
    expect(container.textContent).toContain("v2.1.0");
  });

  it("shows memory usage", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[runningSandbox]} appName="App" />);
    expect(container.textContent).toContain("128/256MB");
  });

  it("shows CPU usage", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[runningSandbox]} appName="App" />);
    expect(container.textContent).toContain("CPU: 12.5s");
  });

  it("shows log line count", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[runningSandbox]} appName="App" />);
    expect(container.textContent).toContain("42 log lines");
  });

  it("shows exit code for stopped sandbox", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[stoppedSandbox]} appName="App" />);
    expect(container.textContent).toContain("Exit: 0");
  });

  it("shows non-zero exit code for terminated sandbox", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[terminatedSandbox]} appName="App" />);
    expect(container.textContent).toContain("Exit: 137");
  });

  it("shows status badges", () => {
    const { container } = render(
      <SandboxEnvCard
        sandboxes={[runningSandbox, stoppedSandbox, terminatedSandbox]}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("stopped");
    expect(container.textContent).toContain("terminated");
  });

  it("shows empty state", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[]} appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
