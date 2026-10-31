import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SessionStoreCard from "../src/components/session-store-card";

const activeSession = {
  session_id: "sess-abc",
  user_id: "user-1",
  created_at: new Date(Date.now() - 1_800_000).toISOString(),
  expires_at: new Date(Date.now() + 1_800_000).toISOString(),
  last_accessed_at: new Date(Date.now() - 120_000).toISOString(),
  revoked: false,
  data_keys: ["role", "theme"],
};

const revokedSession = {
  session_id: "sess-def",
  user_id: "user-2",
  created_at: new Date(Date.now() - 7_200_000).toISOString(),
  expires_at: new Date(Date.now() + 3_600_000).toISOString(),
  last_accessed_at: new Date(Date.now() - 3_600_000).toISOString(),
  revoked: true,
  data_keys: [],
};

const expiredSession = {
  session_id: "sess-ghi",
  user_id: "user-3",
  created_at: new Date(Date.now() - 86_400_000).toISOString(),
  expires_at: new Date(Date.now() - 3_600_000).toISOString(),
  last_accessed_at: new Date(Date.now() - 7_200_000).toISOString(),
  revoked: false,
  data_keys: ["cart"],
};

describe("SessionStoreCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<SessionStoreCard sessions={[activeSession]} appName="My App" />);
    expect(container.textContent).toContain("Sessions");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(
      <SessionStoreCard sessions={[activeSession, revokedSession]} appName="App" />,
    );
    expect(container.textContent).toContain("1 active");
  });

  it("renders user id and session id", () => {
    const { container } = render(<SessionStoreCard sessions={[activeSession]} appName="App" />);
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("sess-abc");
  });

  it("shows revoked label", () => {
    const { container } = render(<SessionStoreCard sessions={[revokedSession]} appName="App" />);
    expect(container.textContent).toContain("revoked");
  });

  it("shows expired label", () => {
    const { container } = render(<SessionStoreCard sessions={[expiredSession]} appName="App" />);
    expect(container.textContent).toContain("expired");
  });

  it("shows last active time", () => {
    const { container } = render(<SessionStoreCard sessions={[activeSession]} appName="App" />);
    expect(container.textContent).toContain("Last active");
  });

  it("shows data key count", () => {
    const { container } = render(<SessionStoreCard sessions={[activeSession]} appName="App" />);
    expect(container.textContent).toContain("2 data keys");
  });

  it("shows empty state", () => {
    const { container } = render(<SessionStoreCard sessions={[]} appName="App" />);
    expect(container.textContent).toContain("No sessions");
  });
});
