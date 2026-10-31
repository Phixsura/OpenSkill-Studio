import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlackPreview } from "@/components/slack-preview";

describe("SlackPreview", () => {
  it("renders message preview", () => {
    const { container } = render(
      <SlackPreview text="🚀 MyApp was published by Alice" channel="#deploys" hasBlocks={true} />
    );
    expect(container.textContent).toContain("OpenSkill Bot");
    expect(container.textContent).toContain("#deploys");
    expect(container.textContent).toContain("MyApp was published");
    expect(container.textContent).toContain("rich blocks");
  });
});
