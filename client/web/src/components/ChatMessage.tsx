import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, User, BarChart3, TrendingUp, ArrowRight } from "lucide-react";

interface ChatMessageProps {
  type: "user" | "agent";
  content: string;
  agentName?: string;
  interactive?: React.ReactNode;
  timestamp?: string;
}

export const ChatMessage = ({ type, content, agentName, interactive, timestamp }: ChatMessageProps) => {
  if (type === "user") {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-[80%] space-y-2">
          <div className="flex items-center justify-end gap-2 text-xs text-muted-foreground">
            <span>You</span>
            <User className="h-4 w-4" />
          </div>
          <div className="bg-primary text-primary-foreground p-4 rounded-2xl rounded-tr-md">
            <p className="text-sm leading-relaxed">{content}</p>
          </div>
          {timestamp && (
            <p className="text-xs text-muted-foreground text-right">{timestamp}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-[85%] space-y-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Brain className="h-4 w-4" />
          <span>{agentName || "AI Agent"}</span>
        </div>
        <div className="bg-card-glass/80 backdrop-blur-sm border border-border/20 p-4 rounded-2xl rounded-tl-md shadow-glass">
          <p className="text-sm leading-relaxed mb-3">{content}</p>
          {interactive && (
            <div className="mt-4">
              {interactive}
            </div>
          )}
        </div>
        {timestamp && (
          <p className="text-xs text-muted-foreground">{timestamp}</p>
        )}
      </div>
    </div>
  );
};

// Interactive Components for Agent Responses
export const VisualizerResponse = ({ onNext }: { onNext: () => void }) => (
  <Card className="bg-card-glass/50 border border-primary/20">
    <CardContent className="p-4 space-y-4">
      <div className="h-40 bg-gradient-card rounded border flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 text-primary mx-auto mb-2" />
          <p className="text-sm font-medium">Tata Motors Q3 Performance</p>
          <div className="flex gap-2 mt-2 justify-center">
            <Badge variant="default">+12.5%</Badge>
            <Badge variant="outline">Volume: 2.3M</Badge>
          </div>
        </div>
      </div>
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground">
          Chart shows strong upward momentum with 12.5% gains this quarter.
        </p>
        <Button 
          size="sm" 
          variant="secondary"
          onClick={onNext}
          className="w-full"
        >
          Show Top 5 Automotive Sector Performers <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </CardContent>
  </Card>
);

export const ScreenerResponse = ({ onNext }: { onNext: () => void }) => (
  <Card className="bg-card-glass/50 border border-accent/20">
    <CardContent className="p-4 space-y-3">
      <p className="text-sm font-medium">Top 5 Automotive Sector Performers</p>
      <div className="space-y-2">
        {[
          { name: "Tata Motors", change: "+15.2%", volume: "2.3M" },
          { name: "Mahindra & Mahindra", change: "+13.1%", volume: "1.8M" },
          { name: "Bajaj Auto", change: "+11.7%", volume: "0.9M" },
          { name: "Hero MotoCorp", change: "+9.4%", volume: "1.2M" },
          { name: "TVS Motor", change: "+8.8%", volume: "0.7M" }
        ].map((stock, i) => (
          <div key={stock.name} className="flex justify-between items-center p-3 rounded bg-card-glass/30 border border-border/10">
            <div>
              <span className="text-sm font-medium">{stock.name}</span>
              <p className="text-xs text-muted-foreground">Vol: {stock.volume}</p>
            </div>
            <Badge variant={i < 2 ? "default" : "secondary"}>
              {stock.change}
            </Badge>
          </div>
        ))}
      </div>
      <Button 
        size="sm" 
        variant="secondary"
        onClick={onNext}
        className="w-full"
      >
        Get Buy/Sell Recommendations <ArrowRight className="h-4 w-4 ml-1" />
      </Button>
    </CardContent>
  </Card>
);

export const RecommenderResponse = ({ onNext }: { onNext: () => void }) => (
  <Card className="bg-card-glass/50 border border-muted/20">
    <CardContent className="p-4 space-y-3">
      <p className="text-sm font-medium">Technical Analysis & Recommendations</p>
      <div className="space-y-3">
        {[
          { name: "Tata Motors", signal: "STRONG BUY", rsi: 45, macd: "Bullish", price: "₹485" },
          { name: "Mahindra & Mahindra", signal: "BUY", rsi: 52, macd: "Bullish", price: "₹1,245" },
          { name: "Bajaj Auto", signal: "HOLD", rsi: 65, macd: "Neutral", price: "₹6,850" }
        ].map((stock) => (
          <div key={stock.name} className="p-3 rounded bg-card-glass/30 border border-border/10 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{stock.name}</span>
              <Badge 
                variant={stock.signal === "STRONG BUY" ? "default" : stock.signal === "BUY" ? "secondary" : "outline"}
              >
                {stock.signal}
              </Badge>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>RSI: {stock.rsi}</div>
              <div>MACD: {stock.macd}</div>
              <div>Price: {stock.price}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button 
          size="sm" 
          variant="buy"
          onClick={() => onNext()}
        >
          Execute Buy Orders
        </Button>
        <Button 
          size="sm" 
          variant="sell"
          onClick={() => onNext()}
        >
          Execute Sell Orders
        </Button>
      </div>
    </CardContent>
  </Card>
);

export const TradingResponse = ({ type, stocks }: { type: "buy" | "sell", stocks: string[] }) => (
  <Card className={`bg-card-glass/50 border ${type === "buy" ? "border-buy/20" : "border-sell/20"}`}>
    <CardContent className="p-4 space-y-3">
      <div className="flex items-center gap-2">
        <div className={`h-2 w-2 rounded-full ${type === "buy" ? "bg-buy" : "bg-sell"}`} />
        <p className="text-sm font-medium">Mock {type === "buy" ? "Purchase" : "Sale"} Executed</p>
      </div>
      {stocks.map((stock, i) => (
        <div key={i} className="flex justify-between items-center p-2 rounded bg-card-glass/30">
          <span className="text-sm">{stock}</span>
          <Badge variant={type === "buy" ? "default" : "destructive"}>
            {type === "buy" ? "✅ Bought" : "💰 Sold"}
          </Badge>
        </div>
      ))}
      <p className="text-xs text-muted-foreground">
        Orders executed successfully. Portfolio updated.
      </p>
    </CardContent>
  </Card>
);