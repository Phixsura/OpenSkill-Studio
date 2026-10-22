import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxIsolationBadge } from "@/components/sandbox-isolation-badge";

describe("SandboxIsolationBadge", () => {
  it("shows isolated", () => {
    const { container } = render(<SandboxIsolationBadge isolated={true} issueCount={0} />);
    expect(container.textContent).toContain("Isolated");
    expect(container.textContent).toContain("🔒");
  });
  it("shows issues", () => {
    const { container } = render(<SandboxIsolationBadge isolated={false} issueCount={3} />);
    expect(container.textContent).toContain("3 issues");
    expect(container.textContent).toContain("⚠️");
  });
});
