import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundEnvList } from "@/components/playground-env-list";

describe("PlaygroundEnvList", () => {
  it("renders envs", () => {
    const { container } = render(
      <PlaygroundEnvList running={1} onCreate={vi.fn()} onStop={vi.fn()} envs={[
        { id: "env_abc", owner: "alice", template: "nextjs", status: "running",
          resources: { cpu: "0.5 vCPU", memory: "512 MB", storage: "1 GB" } },
        { id: "env_xyz", owner: "bob", template: "blank", status: "stopped",
          resources: { cpu: "0.5 vCPU", memory: "512 MB", storage: "1 GB" } },
      ]} />
    );
    expect(container.textContent).toContain("Playgrounds");
    expect(container.textContent).toContain("1 running");
    expect(container.textContent).toContain("env_abc");
    expect(container.textContent).toContain("nextjs");
    expect(container.textContent).toContain("Stop");
    expect(container.textContent).toContain("stopped");
  });
});
