import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPlaygroundSessionCard from "../src/components/api-playground-session-card";

const sessions = [
  { session_id: "s1", user_id: "alice", request_count: 12, active: true },
  { session_id: "s2", user_id: "bob", request_count: 5, active: false },
];

describe("APIPlaygroundSessionCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIPlaygroundSessionCard sessions={sessions} appName="App" />);
    expect(container.textContent).toContain("Playground Sessions");
    expect(container.textContent).toContain("1 active / 2 total");
  });

  it("shows users and request counts", () => {
    const { container } = render(<APIPlaygroundSessionCard sessions={sessions} appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("12 reqs");
  });

  it("shows empty state", () => {
    const { container } = render(<APIPlaygroundSessionCard sessions={[]} appName="App" />);
    expect(container.textContent).toContain("No sessions");
  });
});
