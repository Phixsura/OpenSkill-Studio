import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiff } from "@/components/version-diff";

describe("VersionDiff", () => {
  it("renders diff", () => {
    const { container } = render(
      <VersionDiff oldVersion="1.0.0" newVersion="2.0.0"
        featuresAdded={["webhooks"]} featuresRemoved={[]}
        permissionsAdded={["write:webhooks"]} permissionsRemoved={[]}
        configChanges={[{ key: "port", old: 3000, new: 8080 }]}
        hasBreaking={false} totalChanges={3} />
    );
    expect(container.textContent).toContain("v1.0.0 → v2.0.0");
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("write:webhooks");
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("3 changes");
  });
});
