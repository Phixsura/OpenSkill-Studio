import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OncallSchedule } from "@/components/oncall-schedule";

describe("OncallSchedule", () => {
  it("renders schedule", () => {
    const { container } = render(
      <OncallSchedule oncalls={[
        { oncall: "alice", rotation: "primary", daysRemaining: 5, nextOncall: "bob" },
        { oncall: "carol", rotation: "secondary", daysRemaining: 2, nextOncall: "dave" },
      ]} />
    );
    expect(container.textContent).toContain("On-Call Schedule");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("5d remaining");
    expect(container.textContent).toContain("next: bob");
    expect(container.textContent).toContain("carol");
  });
});
