"use client";
export function FleetStoryblokPanel({ spaces, active, stories, components }: { spaces: number; active: number; stories: number; components: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 Storyblok</h3>
    <div className="text-sm">{active}/{spaces} active · {stories.toLocaleString()} stories · {components} components</div>
  </div>);
}
