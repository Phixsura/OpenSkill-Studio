import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

const rules = [{ ruleId: "ip-1", network: "192.168.1.0/24", description: "Office" }];

describe("IpAllowlistEditor", () => {
  it("renders rules", () => {
    const { container } = render(<IpAllowlistEditor rules={rules} />);
    expect(container.textContent).toContain("192.168.1.0/24");
    expect(container.textContent).toContain("Office");
  });
  it("shows warning when empty", () => {
    const { container } = render(<IpAllowlistEditor rules={[]} />);
    expect(container.textContent).toContain("No IP restrictions");
  });
  it("add rule", () => {
    const fn = vi.fn();
    const { container } = render(<IpAllowlistEditor rules={[]} onAdd={fn} />);
    const inputs = container.querySelectorAll("input");
    fireEvent.change(inputs[0], { target: { value: "10.0.0.0/8" } });
    fireEvent.change(inputs[1], { target: { value: "VPN" } });
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("10.0.0.0/8", "VPN");
  });
});
