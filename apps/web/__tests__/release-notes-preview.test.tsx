import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseNotesPreview } from "@/components/release-notes-preview";

describe("ReleaseNotesPreview", () => {
  const sections = [
    { title: "🚀 New Features", items: ["Dark mode", "Export CSV"] },
    { title: "🐛 Bug Fixes", items: ["Login crash"] },
  ];
  it("renders", () => {
    const { container } = render(
      <ReleaseNotesPreview appName="MyApp" version="2.0.0" sections={sections}
        commitCount={5} onPublish={vi.fn()} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp v2.0.0");
    expect(container.textContent).toContain("5 commits");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Login crash");
  });
  it("publish", () => {
    const fn = vi.fn();
    const { container } = render(
      <ReleaseNotesPreview appName="X" version="1.0" sections={sections}
        commitCount={3} onPublish={fn} onEdit={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Publish")!);
    expect(fn).toHaveBeenCalled();
  });
});
