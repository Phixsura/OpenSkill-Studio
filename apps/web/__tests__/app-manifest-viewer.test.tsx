import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppManifestViewer } from "@/components/app-manifest-viewer";

describe("AppManifestViewer", () => {
  it("renders valid manifest", () => {
    const manifest = { name: "my-app", version: "1.0.0" };
    const { container } = render(
      <AppManifestViewer manifest={manifest} valid={true} errors={[]} warnings={["No icon"]} />
    );
    expect(container.textContent).toContain("app.json");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("my-app");
    expect(container.textContent).toContain("No icon");
  });
  it("renders errors", () => {
    const { container } = render(
      <AppManifestViewer manifest={{}} valid={false} errors={["Missing name"]} warnings={[]} />
    );
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("Missing name");
  });
});
