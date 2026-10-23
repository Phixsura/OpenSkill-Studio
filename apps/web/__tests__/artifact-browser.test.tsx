import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ArtifactBrowser } from "@/components/artifact-browser";

describe("ArtifactBrowser", () => {
  it("renders artifacts", () => {
    const { container } = render(
      <ArtifactBrowser totalSizeMb={120} totalDownloads={500}
        artifacts={[
          { name: "api", version: "1.0.0", sizeMb: 45, digest: "sha256:abc123", downloads: 300 },
          { name: "web", version: "2.1.0", sizeMb: 75, digest: "sha256:def456", downloads: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Build Artifacts");
    expect(container.textContent).toContain("2 artifacts");
    expect(container.textContent).toContain("120 MB");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("1.0.0");
    expect(container.textContent).toContain("sha256:abc123");
  });
});
