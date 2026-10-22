"use client";

interface DeveloperWelcomeBannerProps { developerName: string; appCount: number; isNew: boolean; }

export function DeveloperWelcomeBanner({ developerName, appCount, isNew }: DeveloperWelcomeBannerProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
      <h2 className="text-2xl font-bold">
        {isNew ? `Welcome, ${developerName}! 👋` : `Welcome back, ${developerName}`}
      </h2>
      <p className="mt-1 opacity-80">
        {isNew ? "Start building your first app on OpenSkill" : `You have ${appCount} app${appCount !== 1 ? "s" : ""}`}
      </p>
    </div>
  );
}
