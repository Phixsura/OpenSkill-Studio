import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DevProgramTiers } from "@/components/dev-program-tiers";

describe("DevProgramTiers", () => {
  it("renders tiers", () => {
    const onSelect = vi.fn();
    const { container, getAllByText } = render(
      <DevProgramTiers currentTier="community" onSelect={onSelect} tiers={[
        { id: "community", label: "Community", icon: "🌱", feeDisplay: "Free",
          benefits: ["Listing", "Support"], recommended: false },
        { id: "partner", label: "Partner", icon: "🤝", feeDisplay: "$99/mo",
          benefits: ["Partner badge", "Revenue sharing"], recommended: true },
      ]} />
    );
    expect(container.textContent).toContain("Community");
    expect(container.textContent).toContain("Current");
    expect(container.textContent).toContain("Partner");
    expect(container.textContent).toContain("$99/mo");
    expect(container.textContent).toContain("Recommended");
    fireEvent.click(getAllByText("Select")[0]);
    expect(onSelect).toHaveBeenCalledWith("partner");
  });
});
