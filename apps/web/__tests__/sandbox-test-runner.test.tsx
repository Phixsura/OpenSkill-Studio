import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxTestRunner } from "@/components/sandbox-test-runner";

describe("SandboxTestRunner", () => {
  it("shows results", () => {
    const results = [
      { name: "health check", passed: true, duration_ms: 50 },
      { name: "auth flow", passed: false, duration_ms: 200 },
    ];
    const { container } = render(<SandboxTestRunner results={results} passRate={50} />);
    expect(container.textContent).toContain("health check");
    expect(container.textContent).toContain("50% passed");
    expect(container.textContent).toContain("50ms");
  });
  it("shows running state", () => {
    const { container } = render(<SandboxTestRunner results={[]} passRate={0} isRunning />);
    expect(container.textContent).toContain("Running...");
  });
  it("green on 100%", () => {
    const { container } = render(
      <SandboxTestRunner results={[{ name: "t1", passed: true, duration_ms: 10 }]} passRate={100} />
    );
    expect(container.textContent).toContain("100%");
  });
});
