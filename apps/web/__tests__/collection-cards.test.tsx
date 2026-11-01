import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CollectionCards } from "@/components/collection-cards";

describe("CollectionCards", () => {
  it("renders collections", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <CollectionCards onSelect={onSelect} collections={[
        { title: "DevOps Essentials", description: "Must-have tools", appCount: 5, curator: "admin", featured: true },
        { title: "Analytics Pack", description: "Data insights", appCount: 3, curator: "team", featured: false },
      ]} />
    );
    expect(container.textContent).toContain("DevOps Essentials");
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("5 apps");
    expect(container.textContent).toContain("Analytics Pack");
    fireEvent.click(getByText("DevOps Essentials"));
    expect(onSelect).toHaveBeenCalledWith("DevOps Essentials");
  });
});
