import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogEmailPreview } from "@/components/changelog-email-preview";

describe("ChangelogEmailPreview", () => {
  it("renders", () => {
    const sections = [{ title: "New Features", icon: "✨", items: ["Dark mode"] }];
    const { container } = render(
      <ChangelogEmailPreview subject="MyApp v2.0" sections={sections} totalChanges={3} recipientCount={500} onSend={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp v2.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("500");
  });
  it("sends", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogEmailPreview subject="X" sections={[]} totalChanges={0} recipientCount={100} onSend={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
