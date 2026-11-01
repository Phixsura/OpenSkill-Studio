import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorTrackerPanel } from "@/components/error-tracker-panel";
describe("ErrorTrackerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrorTrackerPanel totalErrors={50} uniqueGroups={5}
        groups={[
          { group: "TypeError:Cannot read property", count: 20 },
          { group: "ValueError:Invalid input", count: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Error Tracker");
    expect(container.textContent).toContain("50 errors");
    expect(container.textContent).toContain("5 groups");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("20x");
  });
});
