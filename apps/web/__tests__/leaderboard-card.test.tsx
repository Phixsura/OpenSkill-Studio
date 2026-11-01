import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LeaderboardCard from "../src/components/leaderboard-card";

const entries = [
  { rank: 1, user_id: "alice", score: 9500 },
  { rank: 2, user_id: "bob", score: 8200 },
  { rank: 3, user_id: "carol", score: 7100 },
  { rank: 4, user_id: "dave", score: 5000 },
];

describe("LeaderboardCard", () => {
  it("renders board name and app name", () => {
    const { container } = render(
      <LeaderboardCard
        entries={entries}
        boardName="Speed Run"
        appName="My App"
        totalPlayers={42}
      />,
    );
    expect(container.textContent).toContain("Speed Run");
    expect(container.textContent).toContain("My App");
  });

  it("shows player count", () => {
    const { container } = render(
      <LeaderboardCard entries={entries} boardName="B" appName="A" totalPlayers={42} />,
    );
    expect(container.textContent).toContain("42 players");
  });

  it("shows medal emojis for top 3", () => {
    const { container } = render(
      <LeaderboardCard entries={entries} boardName="B" appName="A" totalPlayers={4} />,
    );
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("🥈");
    expect(container.textContent).toContain("🥉");
  });

  it("shows hash rank for 4th+", () => {
    const { container } = render(
      <LeaderboardCard entries={entries} boardName="B" appName="A" totalPlayers={4} />,
    );
    expect(container.textContent).toContain("#4");
  });

  it("renders user ids", () => {
    const { container } = render(
      <LeaderboardCard entries={entries} boardName="B" appName="A" totalPlayers={4} />,
    );
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("carol");
  });

  it("shows formatted scores", () => {
    const { container } = render(
      <LeaderboardCard entries={entries} boardName="B" appName="A" totalPlayers={4} />,
    );
    expect(container.textContent).toContain("9.5K");
    expect(container.textContent).toContain("8.2K");
    expect(container.textContent).toContain("5.0K");
  });

  it("shows empty state", () => {
    const { container } = render(
      <LeaderboardCard entries={[]} boardName="B" appName="A" totalPlayers={0} />,
    );
    expect(container.textContent).toContain("No scores yet");
  });
});
