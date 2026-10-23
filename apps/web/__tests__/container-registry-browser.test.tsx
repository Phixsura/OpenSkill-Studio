import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContainerRegistryBrowser } from "@/components/container-registry-browser";

describe("ContainerRegistryBrowser", () => {
  it("renders repos", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <ContainerRegistryBrowser onSelect={onSelect} repos={[
        { name: "myapp", visibility: "private", tagCount: 5, pulls: 120 },
        { name: "base-image", visibility: "public", tagCount: 3, pulls: 5000 },
      ]} />
    );
    expect(container.textContent).toContain("Container Registry");
    expect(container.textContent).toContain("myapp");
    expect(container.textContent).toContain("5 tags");
    expect(container.textContent).toContain("private");
    expect(container.textContent).toContain("public");
    fireEvent.click(getByText("myapp"));
    expect(onSelect).toHaveBeenCalledWith("myapp");
  });
});
