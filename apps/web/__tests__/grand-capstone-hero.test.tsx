import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandCapstoneHero } from "@/components/grand-capstone-hero";

describe("GrandCapstoneHero", () => {
  const stats = { commits: 1500, lines: 132000, files: 3940,
    backend_services: 880, frontend_components: 780, test_files: 1800 };
  const modules = { "Extension SDK": "operational", "Marketplace": "operational",
    "Security": "operational" };
  const techStack = { backend: "Python (FastAPI)", frontend: "React (Next.js)" };
  it("renders the grand capstone", () => {
    const { container } = render(
      <GrandCapstoneHero version="7.0.0" codename="Grand Capstone" stats={stats}
        modules={modules} techStack={techStack} achievement="🎉 Complete!" />
    );
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("v7.0.0");
    expect(container.textContent).toContain("Grand Capstone");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("132,000");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("Python (FastAPI)");
    expect(container.textContent).toContain("🎉 Complete!");
  });
});
