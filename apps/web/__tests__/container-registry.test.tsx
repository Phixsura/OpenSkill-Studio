import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContainerRegistry } from "@/components/container-registry";

describe("ContainerRegistry", () => {
  const images = [
    { name: "api", tag: "v2.1.0", digest: "sha256:abc", sizeMb: 150, pushedAt: "2026-01-02", pullCount: 500 },
  ];
  it("renders images", () => {
    const { container } = render(<ContainerRegistry images={images} totalSizeMb={150} />);
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("150MB");
    expect(container.textContent).toContain("500 pulls");
  });
});
