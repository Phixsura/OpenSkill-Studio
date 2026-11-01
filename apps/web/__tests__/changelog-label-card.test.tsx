import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogLabelCard from "../src/components/changelog-label-card";

const labels = [
  { label_id: "feat", name: "Feature", category: "type", color: "#22c55e", count: 15 },
  { label_id: "bug", name: "Bug Fix", category: "type", color: "#ef4444", count: 8 },
  { label_id: "api", name: "API", category: "scope", color: "#3b82f6", count: 10 },
  { label_id: "breaking", name: "Breaking", category: "impact", color: "#f97316", count: 3 },
];

describe("ChangelogLabelCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ChangelogLabelCard labels={labels} appName="My App" totalEntries={36} />,
    );
    expect(container.textContent).toContain("Changelog Labels");
    expect(container.textContent).toContain("My App");
  });

  it("shows label and entry counts", () => {
    const { container } = render(
      <ChangelogLabelCard labels={labels} appName="App" totalEntries={36} />,
    );
    expect(container.textContent).toContain("4 labels");
    expect(container.textContent).toContain("36 entries");
  });

  it("renders category headers", () => {
    const { container } = render(
      <ChangelogLabelCard labels={labels} appName="App" totalEntries={0} />,
    );
    expect(container.textContent).toContain("type");
    expect(container.textContent).toContain("scope");
    expect(container.textContent).toContain("impact");
  });

  it("renders label names with counts", () => {
    const { container } = render(
      <ChangelogLabelCard labels={labels} appName="App" totalEntries={0} />,
    );
    expect(container.textContent).toContain("Feature");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("Bug Fix");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogLabelCard labels={[]} appName="App" totalEntries={0} />);
    expect(container.textContent).toContain("No labels defined");
  });
});
