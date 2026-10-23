import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Leaderboard } from "@/components/leaderboard";

describe("Leaderboard", () => {
  const entries = [
    { rank: 1, name: "AppB", icon: "🚀", value: 15000, author: "Bob", medal: "🥇" },
    { rank: 2, name: "AppC", icon: "📦", value: 8000, author: "Charlie", medal: "🥈" },
  ];
  it("renders leaderboard", () => {
    const { container } = render(<Leaderboard entries={entries} metric="downloads" period="all_time" />);
    expect(container.textContent).toContain("Top Apps");
    expect(container.textContent).toContain("AppB");
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("by Bob");
  });
});
