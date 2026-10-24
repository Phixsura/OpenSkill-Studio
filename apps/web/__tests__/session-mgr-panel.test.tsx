import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SessionMgrPanel } from "@/components/session-mgr-panel";

describe("SessionMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SessionMgrPanel activeSessions={3} ttlSeconds={3600}
        sessions={[
          { userId: "alice", remaining: 3200 },
          { userId: "bob", remaining: 1800 },
        ]} />
    );
    expect(container.textContent).toContain("Sessions");
    expect(container.textContent).toContain("3 active");
    expect(container.textContent).toContain("3600s TTL");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3200s left");
  });
});
