import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GlobalStatsDisplay } from "@/components/global-stats-display";

const stats = { extensions: 553, developers: 2000, installs: 100000, services: 553, tests: 2750, commits: 4821, avgRating: 4.5, uptime: 99.99 };
const highlights = [{ label: "500+ Extensions", value: 553, metric: "extensions" }];

describe("GlobalStatsDisplay", () => {
  it("renders stats and highlights", () => {
    const { container } = render(<GlobalStatsDisplay stats={stats} highlights={highlights} />);
    expect(container.textContent).toContain("553");
    expect(container.textContent).toContain("2,750");
    expect(container.textContent).toContain("4,821");
    expect(container.textContent).toContain("500+ Extensions");
  });
});
