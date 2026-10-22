import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesView } from "@/components/release-notes-view";

describe("ReleaseNotesView", () => {
  it("shows version", () => {
    const { container } = render(<ReleaseNotesView version="2.0" sections={[{ type: "notes", content: "Big update" }]} breaking={false} />);
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("Big update");
  });
  it("shows breaking", () => {
    const { container } = render(<ReleaseNotesView version="3.0" sections={[]} breaking={true} />);
    expect(container.textContent).toContain("Breaking");
  });
});
