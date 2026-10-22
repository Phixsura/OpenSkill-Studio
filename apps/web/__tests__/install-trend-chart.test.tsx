import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallTrendChart } from "@/components/install-trend-chart";

const DATA = [{ date: "Jan 1", installs: 5, uninstalls: 1, net: 4 }, { date: "Jan 2", installs: 3, uninstalls: 2, net: 1 }];

describe("InstallTrendChart", () => {
  it("shows date range", () => {
    const { container } = render(<InstallTrendChart data={DATA} />);
    expect(container.textContent).toContain("Jan 1");
    expect(container.textContent).toContain("Jan 2");
  });
  it("empty state", () => {
    const { container } = render(<InstallTrendChart data={[]} />);
    expect(container.textContent).toContain("No install data");
  });
});
