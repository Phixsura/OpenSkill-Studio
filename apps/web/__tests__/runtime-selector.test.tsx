import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RuntimeSelector } from "@/components/runtime-selector";

describe("RuntimeSelector", () => {
  it("renders runtimes", () => {
    const { container } = render(<RuntimeSelector selected="python3.12" onChange={vi.fn()} />);
    expect(container.textContent).toContain("Python 3.12");
    expect(container.textContent).toContain("Node.js 20");
  });

  it("highlights selected", () => {
    const { container } = render(<RuntimeSelector selected="nodejs20" onChange={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Node.js 20"));
    expect(btn?.className).toContain("blue");
  });

  it("calls onChange", () => {
    const onChange = vi.fn();
    const { container } = render(<RuntimeSelector selected="python3.12" onChange={onChange} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Node.js 20"));
    fireEvent.click(btn!);
    expect(onChange).toHaveBeenCalledWith("nodejs20");
  });
});
