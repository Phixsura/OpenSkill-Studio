import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishPage } from "@/components/publish-page";

describe("PublishPage", () => {
  const steps = [
    { id: "manifest", label: "Valid Manifest", auto: true, pass: true, icon: "✅" },
    { id: "review", label: "Self Review", auto: false, pass: false, icon: "⏳" },
  ];
  it("renders publish page", () => {
    const { container } = render(
      <PublishPage appName="SuperApp" version="2.0.0" releaseNotes="Big update"
        steps={steps} score={50} canPublish={false} cta="Complete 1 check"
        onPublish={vi.fn()} onEditNotes={vi.fn()} />
    );
    expect(container.textContent).toContain("Publish SuperApp v2.0.0");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Valid Manifest");
    expect(container.textContent).toContain("Complete 1 check");
  });
});
