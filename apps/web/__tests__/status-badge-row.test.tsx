import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadgeRow } from "@/components/status-badge-row";

describe("StatusBadgeRow", () => {
  const badges = [
    { svgUrl: "https://img.shields.io/badge/build-passing-brightgreen", label: "build", value: "passing", color: "brightgreen" },
    { svgUrl: "https://img.shields.io/badge/coverage-95%25-blue", label: "coverage", value: "95%", color: "blue" },
  ];
  it("renders badges", () => {
    const { container } = render(<StatusBadgeRow badges={badges} />);
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("passing");
    expect(container.textContent).toContain("coverage");
    expect(container.textContent).toContain("95%");
  });
});
