import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseCalendar } from "@/components/release-calendar";

describe("ReleaseCalendar", () => {
  it("renders calendar", () => {
    const { container } = render(
      <ReleaseCalendar planned={1} inProgress={1} released={1} totalFeatures={6}
        releases={[
          { version: "3.0", targetDate: "2024-10-01", featureCount: 2, owner: "alice", status: "released" },
          { version: "4.0", targetDate: "2025-01-15", featureCount: 3, owner: "bob", status: "planned" },
        ]} />
    );
    expect(container.textContent).toContain("Release Calendar");
    expect(container.textContent).toContain("1 released");
    expect(container.textContent).toContain("1 planned");
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("v4.0");
    expect(container.textContent).toContain("3 features");
  });
});
