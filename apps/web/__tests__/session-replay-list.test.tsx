import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SessionReplayList } from "@/components/session-replay-list";

describe("SessionReplayList", () => {
  const sessions = [
    { sessionId: "s1", pageUrl: "/dashboard", durationDisplay: "2m 5s", events: 50, errors: 0, hasErrors: false },
    { sessionId: "s2", pageUrl: "/settings", durationDisplay: "0m 30s", events: 10, errors: 2, hasErrors: true },
  ];
  it("renders sessions", () => {
    const { container } = render(
      <SessionReplayList sessions={sessions} total={2} avgDurationS={90} errorSessions={1} />
    );
    expect(container.textContent).toContain("/dashboard");
    expect(container.textContent).toContain("2m 5s");
    expect(container.textContent).toContain("1 with errors");
    expect(container.textContent).toContain("2 sessions");
  });
});
