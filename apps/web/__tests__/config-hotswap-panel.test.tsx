import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigHotswapPanel } from "@/components/config-hotswap-panel";

describe("ConfigHotswapPanel", () => {
  it("renders panel", () => {
    const { container } = render(
      <ConfigHotswapPanel activeHash="abc123" pendingHash="def456"
        activeKeyCount={5} hasPending={true} onActivate={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Config Hot-Swap");
    expect(container.textContent).toContain("5 keys");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("def456");
    expect(container.textContent).toContain("Activate");
    expect(container.textContent).toContain("Rollback");
  });
});
