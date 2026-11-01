import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployManifestViewer } from "@/components/deploy-manifest-viewer";

describe("DeployManifestViewer", () => {
  it("renders with diff", () => {
    const { container } = render(
      <DeployManifestViewer valid={true} errors={[]} serviceCount={3}
        diff={{ added: ["new-svc"], removed: ["old-svc"],
                changed: [{ service: "api", newImage: "api:2.0" }] }} />
    );
    expect(container.textContent).toContain("Deploy Manifest");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("+ new-svc");
    expect(container.textContent).toContain("- old-svc");
    expect(container.textContent).toContain("~ api");
  });
});
