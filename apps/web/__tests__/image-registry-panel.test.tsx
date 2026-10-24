import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImageRegistryPanel } from "@/components/image-registry-panel";
describe("ImageRegistryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ImageRegistryPanel totalImages={2} totalTags={4} totalSizeMb={500}
        images={[
          { name: "api", tags: ["v1.0", "v2.0", "latest"], totalSizeMb: 300 },
          { name: "web", tags: ["latest"], totalSizeMb: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Image Registry");
    expect(container.textContent).toContain("2 images");
    expect(container.textContent).toContain("4 tags");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("v2.0");
  });
});
