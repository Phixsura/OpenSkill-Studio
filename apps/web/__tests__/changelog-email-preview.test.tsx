import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogEmailPreview } from "@/components/changelog-email-preview";

describe("ChangelogEmailPreview", () => {
  it("renders", () => {
    const { container } = render(
      <ChangelogEmailPreview subject="MyApp v2.0" bodyHtml="<p>Changes</p>"
        recipientCount={500} changeCount={3} hasBreaking={true}
        onSend={vi.fn()} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("Email Preview");
    expect(container.textContent).toContain("MyApp v2.0");
    expect(container.textContent).toContain("500 recipients");
    expect(container.textContent).toContain("⚠️ Breaking");
    expect(container.textContent).toContain("Changes");
  });
  it("send", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogEmailPreview subject="X" bodyHtml="" recipientCount={10}
        changeCount={1} hasBreaking={false} onSend={fn} onEdit={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Send"))!);
    expect(fn).toHaveBeenCalled();
  });
});
