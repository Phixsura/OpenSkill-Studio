import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

describe("IpAllowlistEditor", () => {
  it("renders entries", () => {
    const { container } = render(<IpAllowlistEditor entries={["10.0.0.0/24"]} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("10.0.0.0/24");
  });
  it("empty state", () => {
    const { container } = render(<IpAllowlistEditor entries={[]} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("all IPs allowed");
  });
  it("calls onRemove", () => {
    const fn = vi.fn();
    const { container } = render(<IpAllowlistEditor entries={["1.2.3.4"]} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(container.querySelector("button:last-child")!);
    expect(fn).toHaveBeenCalledWith("1.2.3.4");
  });
});
