import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RequestReplayPanel } from "@/components/request-replay-panel";

describe("RequestReplayPanel", () => {
  it("renders captures", () => {
    const { container } = render(
      <RequestReplayPanel onReplay={vi.fn()} onClear={vi.fn()} captures={[
        { id: "abc", method: "POST", path: "/api/v1/users" },
        { id: "def", method: "GET", path: "/api/v1/status" },
      ]} />
    );
    expect(container.textContent).toContain("Request Replay");
    expect(container.textContent).toContain("2 captured");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("Replay");
  });
});
