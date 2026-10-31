import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogLabelCard from "../src/components/api-changelog-label-card";

const labels = [
  { label_id: "l1", name: "Bug Fix", color: "#FF0000" },
  { label_id: "l2", name: "Feature", color: "#00FF00" },
];

describe("APIChangelogLabelCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIChangelogLabelCard labels={labels} appName="App" />);
    expect(container.textContent).toContain("Changelog Labels");
    expect(container.textContent).toContain("2 labels");
  });

  it("shows label names", () => {
    const { container } = render(<APIChangelogLabelCard labels={labels} appName="App" />);
    expect(container.textContent).toContain("Bug Fix");
    expect(container.textContent).toContain("Feature");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangelogLabelCard labels={[]} appName="App" />);
    expect(container.textContent).toContain("No labels");
  });
});
