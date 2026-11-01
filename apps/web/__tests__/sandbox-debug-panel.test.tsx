import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxDebugPanel } from "@/components/sandbox-debug-panel";

describe("SandboxDebugPanel", () => {
  it("shows success", () => {
    const { container } = render(<SandboxDebugPanel executionId="exec_123" functionName="process" durationMs={150} success={true} logCount={5} error={null} envCount={3} />);
    expect(container.textContent).toContain("process");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("OK");
  });
  it("shows error", () => {
    const { container } = render(<SandboxDebugPanel executionId="x" functionName="f" durationMs={0} success={false} logCount={0} error="TimeoutError" envCount={0} />);
    expect(container.textContent).toContain("TimeoutError");
    expect(container.textContent).toContain("Failed");
  });
});
