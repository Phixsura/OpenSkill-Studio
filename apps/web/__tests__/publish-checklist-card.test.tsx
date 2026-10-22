import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishChecklistCard } from "@/components/publish-checklist-card";

describe("PublishChecklistCard", () => {
  it("shows ready", () => {
    const { container } = render(<PublishChecklistCard canPublish={true} errors={[]} warnings={[]} onPublish={vi.fn()} />);
    expect(container.textContent).toContain("Ready to Publish");
    expect(container.textContent).toContain("Publish to Marketplace");
  });
  it("shows errors", () => {
    const { container } = render(<PublishChecklistCard canPublish={false} errors={["Missing description"]} warnings={[]} />);
    expect(container.textContent).toContain("Missing description");
    expect(container.textContent).toContain("Not Ready");
  });
  it("shows warnings", () => {
    const { container } = render(<PublishChecklistCard canPublish={true} errors={[]} warnings={["Add icon"]} />);
    expect(container.textContent).toContain("Add icon");
  });
});
