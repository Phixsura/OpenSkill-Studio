import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContainerRegistryBrowser } from "@/components/container-registry-browser";

describe("ContainerRegistryBrowser", () => {
  it("renders images", () => {
    const { container } = render(
      <ContainerRegistryBrowser totalImages={3} totalSizeMb={375} repositories={2} onDelete={vi.fn()}
        images={[
          { name: "myapp", tag: "latest", digest: "sha256:abc123", sizeMb: 150, layers: 5 },
          { name: "worker", tag: "v1.0", digest: "sha256:def456", sizeMb: 80, layers: 3 },
        ]} />
    );
    expect(container.textContent).toContain("Container Registry");
    expect(container.textContent).toContain("3 images");
    expect(container.textContent).toContain("myapp");
    expect(container.textContent).toContain("latest");
    expect(container.textContent).toContain("sha256:abc123");
    expect(container.textContent).toContain("worker");
  });
});
