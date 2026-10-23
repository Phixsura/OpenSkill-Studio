import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

describe("IpAllowlistEditor", () => {
  const rules = [
    { cidr: "10.0.0.0/8", label: "Internal", valid: true, numHosts: 16777216 },
    { cidr: "bad", label: "Broken", valid: false, numHosts: 0 },
  ];
  it("renders rules", () => {
    const { container } = render(<IpAllowlistEditor rules={rules} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("Internal");
    expect(container.textContent).toContain("Invalid");
  });
  it("remove click", () => {
    const fn = vi.fn();
    const { container } = render(<IpAllowlistEditor rules={rules} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("10.0.0.0/8");
  });
});
