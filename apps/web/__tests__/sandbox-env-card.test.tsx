import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SandboxEnvCard from "../src/components/sandbox-env-card";

const sandboxes = [
  { sandbox_id: "sb1", name: "Dev", status: "running" as const, cpu_limit: 2, memory_mb: 1024 },
  { sandbox_id: "sb2", name: "Test", status: "stopped" as const, cpu_limit: 1, memory_mb: 512 },
];

describe("SandboxEnvCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <SandboxEnvCard sandboxes={sandboxes} runningCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Sandboxes");
    expect(container.textContent).toContain("1 running / 2 total");
  });

  it("shows names and status", () => {
    const { container } = render(
      <SandboxEnvCard sandboxes={sandboxes} runningCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Dev");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("stopped");
  });

  it("shows resource limits", () => {
    const { container } = render(
      <SandboxEnvCard sandboxes={sandboxes} runningCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("2 CPU");
    expect(container.textContent).toContain("1024MB");
  });

  it("shows empty state", () => {
    const { container } = render(<SandboxEnvCard sandboxes={[]} runningCount={0} appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
