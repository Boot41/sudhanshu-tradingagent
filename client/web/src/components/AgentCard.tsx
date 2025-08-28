import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LucideIcon } from "lucide-react";

interface AgentCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  status: "idle" | "processing" | "completed";
  result?: React.ReactNode;
  onAction?: () => void;
  actionLabel?: string;
  variant?: "visualizer" | "screener" | "recommender" | "buy" | "sell" | "orchestrator";
}

export const AgentCard = ({
  title,
  description,
  icon: Icon,
  status,
  result,
  onAction,
  actionLabel = "Execute",
  variant = "orchestrator"
}: AgentCardProps) => {
  const getStatusColor = () => {
    switch (status) {
      case "processing": return "bg-primary";
      case "completed": return "bg-buy";
      default: return "bg-muted";
    }
  };

  const getVariantColors = () => {
    switch (variant) {
      case "buy": return "border-buy/20 bg-buy/5";
      case "sell": return "border-sell/20 bg-sell/5";
      case "visualizer": return "border-primary/20 bg-primary/5";
      case "screener": return "border-accent/20 bg-accent/5";
      case "recommender": return "border-muted/20 bg-muted/5";
      default: return "border-border/20 bg-card-glass/50";
    }
  };

  return (
    <Card className={`relative backdrop-blur-sm border shadow-glass transition-all duration-300 hover:shadow-primary/10 hover:scale-[1.02] animate-scale-in ${getVariantColors()}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-card-glass">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <CardDescription className="text-sm">{description}</CardDescription>
            </div>
          </div>
          <Badge
            className={`h-2 w-2 rounded-full p-0 ${getStatusColor()} ${
              status === "processing" ? "animate-agent-pulse" : ""
            }`}
            aria-label={`Status: ${status}`}
          />
        </div>
      </CardHeader>
      
      {result && (
        <CardContent className="pt-0">
          <div className="rounded-lg bg-card-glass/30 p-4 border border-border/10">
            {result}
          </div>
        </CardContent>
      )}
      
      {onAction && status === "idle" && (
        <CardContent className="pt-0">
          <Button
            onClick={onAction}
            variant={variant === "buy" ? "buy" : variant === "sell" ? "sell" : "secondary"}
            className="w-full"
          >
            {actionLabel}
          </Button>
        </CardContent>
      )}
    </Card>
  );
};