import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppListItem } from "@/components/app-list-item";

describe("AppListItem", () => {
  it("shows app info", () => {
    const { container } = render(<AppListItem name="My App" slug="my-app" status="published" category="connector" installCount={42} healthScore={95} needsAttention={false} />);
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("95%");
  });
  it("shows attention indicator", () => {
    const { container } = render(<AppListItem name="Bad" slug="bad" status="rejected" category="automation" installCount={0} healthScore={50} needsAttention={true} />);
    expect(container.textContent).toContain("⚠️");
  });
});
