import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesCard } from "@/components/release-notes-card";

describe("ReleaseNotesCard", () => {
  it("shows version", () => {
    const { container } = render(<ReleaseNotesCard version="2.0.0" date="2026-10" changes={[]} />);
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows changes", () => {
    const { container } = render(<ReleaseNotesCard version="1.0" date="now" changes={[{type: "added", description: "New feature"}]} />);
    expect(container.textContent).toContain("New feature");
    expect(container.textContent).toContain("✨");
  });

  it("shows breaking badge", () => {
    const { container } = render(<ReleaseNotesCard version="3.0" date="now" changes={[]} breaking />);
    expect(container.textContent).toContain("Breaking");
  });

  it("shows date", () => {
    const { container } = render(<ReleaseNotesCard version="1.0" date="2026-10-23" changes={[]} />);
    expect(container.textContent).toContain("2026-10-23");
  });

  it("empty changes text", () => {
    const { container } = render(<ReleaseNotesCard version="1.0" date="now" changes={[]} />);
    expect(container.textContent).toContain("No changes");
  });
});
