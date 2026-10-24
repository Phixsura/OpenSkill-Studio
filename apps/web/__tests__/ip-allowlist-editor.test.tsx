import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

describe("IpAllowlistEditor", () => {
  it("renders entries", () => {
    const { container } = render(
      <IpAllowlistEditor validCount={2} invalidCount={1} onAdd={vi.fn()} onRemove={vi.fn()}
        entries={[
          { address: "10.0.0.0/8", valid: true, isPrivate: true },
          { address: "192.168.1.1", valid: true, isPrivate: true },
          { address: "bad", valid: false },
        ]} />
    );
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("2 valid");
    expect(container.textContent).toContain("1 invalid");
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("private");
    expect(container.textContent).toContain("Add IP/CIDR");
  });
});
