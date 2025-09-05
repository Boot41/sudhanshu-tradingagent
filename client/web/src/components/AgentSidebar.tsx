import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Eye, Filter, Target, ShoppingCart, DollarSign, ArrowDown, BarChart3, TrendingUp, Newspaper, Users } from "lucide-react";

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
    <div className="w-100 border-l border-border/20 bg-card-glass/30 backdrop-blur-sm h-full">
      {/* What We Deliver - Main Section */}
      <div className="p-6 h-full overflow-y-auto">
        <div className="p-6 rounded-lg bg-gradient-to-b from-primary/10 to-primary/5 border border-primary/20">
          <h2 className="text-lg font-bold mb-6 text-center">What We Deliver</h2>
          
          <div className="space-y-4">
            {/* User Input */}
            <div className="flex items-center justify-center gap-4 p-3 rounded-lg bg-card-glass/30">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Target className="h-5 w-5 text-primary" />
              </div>
              <div className="mr-10 min-w-0 ">
                <p className="text-sm font-semibold">Name any company</p>
                <p className="text-sm text-muted-foreground">We handle the rest</p>
              </div>
            </div>
            
            <div className="flex justify-center">
              <ArrowDown className="h-5 w-5 text-muted-foreground" />
            </div>
            
            {/* Comprehensive Analysis */}
            <div className="p-4 rounded-lg bg-card-glass/40 border border-border/10">
              <p className="text-sm font-semibold mb-3 text-center">Comprehensive Analysis</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 p-2 rounded bg-card-glass/30">
                  <BarChart3 className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Financial Health</span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded bg-card-glass/30">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Price Trends</span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded bg-card-glass/30">
                  <Newspaper className="h-4 w-4 text-orange-500" />
                  <span className="text-sm">Market News</span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded bg-card-glass/30">
                  <Users className="h-4 w-4 text-purple-500" />
                  <span className="text-sm">Market Sentiment</span>
                </div>
              </div>
            </div>
            
            <div className="flex justify-center">
              <ArrowDown className="h-5 w-5 text-muted-foreground" />
            </div>
            
            {/* Balanced Perspective */}
            <div className="flex gap-2">
              <div className="flex-1 w-[49%] p-1 py-2 rounded-lg bg-green-500/10 border border-green-500/20">
                <div className="flex items-center gap-2 mb-2">
                  {/* <div className="w-5  h-5 rounded-full bg-green-500/30 flex items-center justify-center">
                    <span className="text-sm">📈</span>
                  </div> */}
                  <span className="text-sm font-semibold">Opportunities</span>
                </div>
                <p className="text-sm text-muted-foreground">Growth potential</p>
              </div>
              <div className="flex-1 w-[49%] p-1 py-2 rounded-lg bg-red-500/10 border border-red-500/20">
                <div className="flex items-center gap-2 mb-2">
                  {/* <div className="w-5 h-5 rounded-full bg-red-500/30 flex items-center justify-center">
                    <span className="text-sm">⚠️</span>
                  </div> */}
                  <span className="text-sm font-semibold">Risks</span>
                </div>
                <p className="text-sm text-muted-foreground">Potential concerns</p>
              </div>
            </div>
            
            <div className="flex justify-center">
              <ArrowDown className="h-5 w-5 text-muted-foreground" />
            </div>
            
            {/* Smart Recommendation */}
            <div className="flex items-center gap-4 p-3 rounded-lg bg-card-glass/30">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Brain className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold">Smart Recommendation</p>
                <p className="text-sm text-muted-foreground">Balanced final assessment</p>
              </div>
            </div>
            
            <div className="flex justify-center">
              <ArrowDown className="h-5 w-5 text-muted-foreground" />
            </div>
            
            {/* Trading Decision */}
            <div className="flex items-center gap-4 p-3 rounded-lg bg-primary/10 border border-primary/20">
              <div className="w-10 h-10 rounded-full bg-primary/30 flex items-center justify-center flex-shrink-0">
                <DollarSign className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold">Clear Trading Signal</p>
                <p className="text-sm text-muted-foreground font-medium">BUY • SELL • HOLD</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};