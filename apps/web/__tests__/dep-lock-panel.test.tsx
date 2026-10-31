import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DepLockPanel } from "@/components/dep-lock-panel";

const mockDeps = [
  { name: "react", version: "18.0", integrity: "sha256-abc123" },
  { name: "lodash", version: "4.17", integrity: "sha256-def456" },
];
const mockDrift = { inSync: false, added: ["axios"], removed: [], changed: ["react"] };

describe("DepLockPanel", () => {
  it("renders locked deps", () => {
    const { container } = render(<DepLockPanel deps={mockDeps} drift={null} lockHash="abc123" />);
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("sha256-abc123");
  });

  it("shows drift", () => {
    const { container } = render(<DepLockPanel deps={mockDeps} drift={mockDrift} lockHash="x" />);
    expect(container.textContent).toContain("Drift");
    expect(container.textContent).toContain("+1");
  });

  it("calls onVerify", () => {
    const onVerify = vi.fn();
    const { getByText } = render(<DepLockPanel deps={[]} drift={null} lockHash="" onVerify={onVerify} />);
    fireEvent.click(getByText("Verify"));
    expect(onVerify).toHaveBeenCalled();
  });
});
