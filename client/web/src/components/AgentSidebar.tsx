import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Eye, Filter, Target, ShoppingCart, DollarSign } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  icon: any;
  status: "idle" | "processing" | "completed";
  description: string;
}

interface AgentSidebarProps {
  agents: Agent[];
}

export const AgentSidebar = ({ agents }: AgentSidebarProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "processing": return "bg-primary animate-agent-pulse";
      case "completed": return "bg-buy";
      default: return "bg-muted";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "processing": return "Working...";
      case "completed": return "Complete";
      default: return "Ready";
    }
  };

  return (
    <div className="w-80 border-l border-border/20 bg-card-glass/30 backdrop-blur-sm">
      <div className="p-6 border-b border-border/20">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          AI Agents
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Specialized trading intelligence
        </p>
      </div>
      
      <div className="p-6 space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto">
        {agents.map((agent) => {
          const Icon = agent.icon;
          return (
            <Card key={agent.id} className="bg-card-glass/50 border border-border/10 hover:bg-card-glass/70 transition-all duration-200">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-card-glass/50">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-sm">{agent.name}</CardTitle>
                    </div>
                  </div>
                  <Badge
                    className={`h-2 w-2 rounded-full p-0 ${getStatusColor(agent.status)}`}
                    aria-label={`Status: ${agent.status}`}
                  />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-xs text-muted-foreground mb-2">{agent.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground">
                    {getStatusText(agent.status)}
                  </span>
                </div>
              </CardContent>
            </Card>
          );
        })}
        
        <div className="mt-6 p-4 rounded-lg bg-primary/10 border border-primary/20">
          <h3 className="text-sm font-medium mb-2">How it works</h3>
          <div className="space-y-2 text-xs text-muted-foreground">
            <p>• Ask for charts, analysis, or trading actions</p>
            <p>• Agents work together automatically</p>
            <p>• Approve each step before execution</p>
            <p>• All interactions happen in chat</p>
          </div>
        </div>
      </div>
    </div>
  );
};