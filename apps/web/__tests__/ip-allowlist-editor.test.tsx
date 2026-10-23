import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

describe("IpAllowlistEditor", () => {
  const entries = [
    { entry: "10.0.0.0/8", normalized: "10.0.0.0/8", version: 4, num_addresses: 16777216 },
  ];
  it("renders", () => {
    const { container } = render(<IpAllowlistEditor entries={entries} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("IPv4");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(<IpAllowlistEditor entries={entries} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove")!);
    expect(fn).toHaveBeenCalledWith("10.0.0.0/8");
  });
});
