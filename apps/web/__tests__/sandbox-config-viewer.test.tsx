import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxConfigViewer } from "@/components/sandbox-config-viewer";

describe("SandboxConfigViewer", () => {
  it("shows runtime", () => {
    const { container } = render(<SandboxConfigViewer runtime="python3.12" memoryMb={256} timeoutSeconds={60} />);
    expect(container.textContent).toContain("python3.12");
  });

  it("shows memory", () => {
    const { container } = render(<SandboxConfigViewer runtime="x" memoryMb={512} timeoutSeconds={30} />);
    expect(container.textContent).toContain("512 MB");
  });

  it("shows timeout", () => {
    const { container } = render(<SandboxConfigViewer runtime="x" memoryMb={128} timeoutSeconds={120} />);
    expect(container.textContent).toContain("120s");
  });

  it("shows allowed hosts", () => {
    const { container } = render(<SandboxConfigViewer runtime="x" memoryMb={128} timeoutSeconds={30}
      network={{ allowedHosts: ["api.example.com", "hooks.slack.com"], egressPolicy: "allowlist" }} />);
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("hooks.slack.com");
  });

  it("shows egress policy", () => {
    const { container } = render(<SandboxConfigViewer runtime="x" memoryMb={128} timeoutSeconds={30}
      network={{ allowedHosts: [], egressPolicy: "allowlist" }} />);
    expect(container.textContent).toContain("allowlist");
  });
});
