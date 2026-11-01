import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundHistoryPanel } from "@/components/playground-history-panel";

const reqs = [
  { requestId: "r1", name: "List Users", method: "GET", url: "/api/users", responseStatus: 200, timestamp: "5m ago" },
  { requestId: "r2", name: "Create Item", method: "POST", url: "/api/items", responseStatus: 201, timestamp: "10m ago" },
];
const cols = [{ collectionId: "c1", name: "User API", requestCount: 5 }];

describe("PlaygroundHistoryPanel", () => {
  it("renders history", () => {
    const { container } = render(<PlaygroundHistoryPanel requests={reqs} collections={cols} />);
    expect(container.textContent).toContain("List Users");
    expect(container.textContent).toContain("200");
  });
  it("calls onReplay", () => {
    const fn = vi.fn();
    const { getAllByText } = render(<PlaygroundHistoryPanel requests={reqs} collections={cols} onReplay={fn} />);
    fireEvent.click(getAllByText("Replay")[0]);
    expect(fn).toHaveBeenCalledWith("r1");
  });
  it("shows collections", () => {
    const { getByText, container } = render(<PlaygroundHistoryPanel requests={reqs} collections={cols} />);
    fireEvent.click(getByText("Collections (1)"));
    expect(container.textContent).toContain("User API");
    expect(container.textContent).toContain("5 requests");
  });
});
