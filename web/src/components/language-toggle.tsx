"use client";

import { Languages } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useLocale } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

type LanguageToggleProps = {
  className?: string;
};

export function LanguageToggle({ className }: LanguageToggleProps) {
  const { locale, setLocale } = useLocale();

  const isZh = locale === "zh";
  const targetLocale = isZh ? "en" : "zh";
  const tooltipText = isZh ? "Switch UI to English (reloads page)" : "Switch UI to 中文 (reloads page)";

  const handleToggle = () => {
    setLocale(targetLocale);
    window.location.reload();
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label="Switch language"
            className={cn("relative", className)}
            onClick={handleToggle}
          >
            <Languages className="size-4" />
            <span
              className={cn(
                "pointer-events-none absolute -right-0.5 -bottom-0.5 rounded px-0.5 font-semibold text-[9px] leading-none",
                "border border-border bg-muted text-foreground shadow-xs",
              )}
            >
              {isZh ? "中" : "EN"}
            </span>
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">{tooltipText}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
