import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseManagerPage } from "@/components/release-manager-page";

describe("ReleaseManagerPage", () => {
  const stages = ["draft", "testing", "review", "approved", "published"];
  it("renders release flow", () => {
    const { container } = render(
      <ReleaseManagerPage appName="SuperApp" version="3.0.0" stage="testing"
        stages={stages} changelog="Big update" breaking={true}
        onAdvance={vi.fn()} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("Release SuperApp v3.0.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("Big update");
    expect(container.textContent).toContain("Advance to review");
  });
});
