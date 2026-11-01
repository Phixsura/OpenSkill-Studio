import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SessionManagerCard from "../src/components/session-manager-card";

const sessions = [
  {
    session_id: "s1",
    user_id: "alice",
    is_active: true,
    ip_address: "10.0.0.1",
    user_agent: "Chrome",
  },
  {
    session_id: "s2",
    user_id: "bob",
    is_active: false,
    ip_address: "10.0.0.2",
    user_agent: "Firefox",
  },
];

describe("SessionManagerCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <SessionManagerCard sessions={sessions} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Sessions");
    expect(container.textContent).toContain("1 active / 2 total");
  });

  it("shows user IDs", () => {
    const { container } = render(
      <SessionManagerCard sessions={sessions} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
  });

  it("shows IP addresses", () => {
    const { container } = render(
      <SessionManagerCard sessions={sessions} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("10.0.0.1");
  });

  it("shows empty state", () => {
    const { container } = render(
      <SessionManagerCard sessions={[]} activeCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No sessions");
  });
});
