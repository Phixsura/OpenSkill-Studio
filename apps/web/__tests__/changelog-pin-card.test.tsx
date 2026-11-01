import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogPinCard from "../src/components/changelog-pin-card";

const pins = [
  {
    entry_id: "e1",
    version: "2.0.0",
    title: "Breaking API change",
    reason: "Migration required",
    pinned_by: "admin",
  },
  { entry_id: "e2", version: "1.5.0", title: "Security patch", reason: "", pinned_by: "" },
];

describe("ChangelogPinCard", () => {
  it("renders header", () => {
    const { container } = render(<ChangelogPinCard pins={pins} maxPins={10} appName="My App" />);
    expect(container.textContent).toContain("Pinned Changes");
  });

  it("shows pin count", () => {
    const { container } = render(<ChangelogPinCard pins={pins} maxPins={10} appName="App" />);
    expect(container.textContent).toContain("2/10 pinned");
  });

  it("renders titles and versions", () => {
    const { container } = render(<ChangelogPinCard pins={pins} maxPins={10} appName="App" />);
    expect(container.textContent).toContain("Breaking API change");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows reason and pinned by", () => {
    const { container } = render(<ChangelogPinCard pins={pins} maxPins={10} appName="App" />);
    expect(container.textContent).toContain("Migration required");
    expect(container.textContent).toContain("pinned by admin");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogPinCard pins={[]} maxPins={10} appName="App" />);
    expect(container.textContent).toContain("No pinned entries");
  });
});
