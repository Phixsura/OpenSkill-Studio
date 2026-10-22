import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MockServerPanel } from "@/components/mock-server-panel";

describe("MockServerPanel", () => {
  it("renders endpoints", () => {
    const eps = [{ path: "/users", method: "GET", status_code: 200 }];
    const { container } = render(<MockServerPanel endpoints={eps} port={3001} isRunning={true} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain(":3001");
    expect(container.textContent).toContain("Stop");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const { container } = render(<MockServerPanel endpoints={[]} port={3001} isRunning={false} onToggle={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
