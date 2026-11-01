import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundHistory } from "@/components/playground-history";

describe("PlaygroundHistory", () => {
  it("renders history", () => {
    const history = [
      { request: { method: "GET", path: "/users" }, response: { status: 200 }, timestamp: "" },
      { request: { method: "POST", path: "/apps" }, response: { status: 500 }, timestamp: "" },
    ];
    const { container } = render(<PlaygroundHistory history={history} onReplay={vi.fn()} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("500");
  });
  it("empty state", () => {
    const { container } = render(<PlaygroundHistory history={[]} onReplay={vi.fn()} />);
    expect(container.textContent).toContain("No request history");
  });
  it("replay", () => {
    const fn = vi.fn();
    const history = [{ request: {}, response: {}, timestamp: "" }];
    const { container } = render(<PlaygroundHistory history={history} onReplay={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
