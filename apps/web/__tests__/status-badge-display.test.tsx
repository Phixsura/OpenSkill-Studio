import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadgeDisplay } from "@/components/status-badge-display";

describe("StatusBadgeDisplay", () => {
  it("renders badges", () => {
    const { container } = render(
      <StatusBadgeDisplay badges={[
        { label: "build", value: "passing", color: "green" },
        { label: "version", value: "v3.0.1", color: "blue" },
        { label: "uptime", value: "99.95%", color: "green" },
      ]} />
    );
    expect(container.textContent).toContain("Status Badges");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("passing");
    expect(container.textContent).toContain("v3.0.1");
    expect(container.textContent).toContain("99.95%");
  });
});
