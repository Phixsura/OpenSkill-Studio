import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CollectionCard } from "@/components/collection-card";

describe("CollectionCard", () => {
  it("renders collection info", () => {
    const { container } = render(
      <CollectionCard title="Best Tools" description="Top picks" appCount={5} slug="best-tools"
        previewApps={[{ name: "App1", icon: "🔧" }, { name: "App2" }]} />
    );
    expect(container.textContent).toContain("Best Tools");
    expect(container.textContent).toContain("5 apps");
    expect(container.textContent).toContain("+3");
  });
  it("links to collection page", () => {
    const { container } = render(
      <CollectionCard title="T" description="D" appCount={3} slug="my-col" previewApps={[]} />
    );
    const link = container.querySelector("a");
    expect(link?.getAttribute("href")).toBe("/marketplace/collections/my-col");
  });
});
