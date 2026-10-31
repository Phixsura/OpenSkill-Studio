import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-request-replay-card";

describe("RequestReplayCard", () => {
  it("shows stats and recent", () => {
    const { container } = render(<Card stats={{ captured: 100, replayed: 50, successful: 45 }} recent={[{ request_id: "r1", method: "POST", path: "/users", original_status: 201 }]} appName="App" />);
    expect(container.textContent).toContain("Request Replay");
    expect(container.textContent).toContain("90.0% success");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/users");
  });
  it("handles zero replays", () => {
    const { container } = render(<Card stats={{ captured: 0, replayed: 0, successful: 0 }} recent={[]} appName="App" />);
    expect(container.textContent).toContain("—% success");
  });
});
