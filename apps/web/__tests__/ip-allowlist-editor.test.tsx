import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpAllowlistEditor } from "@/components/ip-allowlist-editor";

describe("IpAllowlistEditor", () => {
  it("renders and removes", () => {
    const onRemove = vi.fn();
    const { container, getByText } = render(
      <IpAllowlistEditor onAdd={vi.fn()} onRemove={onRemove} rules={[
        { cidr: "10.0.0.0/8", label: "Internal", enabled: true, hosts: 16777216 },
      ]} />
    );
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("Internal");
    fireEvent.click(getByText("Remove"));
    expect(onRemove).toHaveBeenCalledWith("10.0.0.0/8");
  });
});
