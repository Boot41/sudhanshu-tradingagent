import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChatMessage, VisualizerResponse, ScreenerResponse, RecommenderResponse, TradingResponse } from "@/components/ChatMessage";
import { AgentSidebar } from "@/components/AgentSidebar";
import { 
  Brain, Eye, Filter, Target, ShoppingCart, DollarSign, 
  Send, LogOut, Sparkles, ArrowRight 
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  agentName?: string;
  interactive?: React.ReactNode;
  timestamp: string;
}

interface Agent {
  id: string;
  name: string;
  icon: any;
  status: "idle" | "processing" | "completed";
  description: string;
}

const Playground = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };
  
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "orchestrator",
      name: "Orchestrator",
      icon: Brain,
      status: "idle",
      description: "Coordinates workflow between agents"
    },
    {
      id: "visualizer",
      name: "Visualizer",
      icon: Eye,
      status: "idle",
      description: "Creates charts and visual analysis"
    },
    {
      id: "screener",
      name: "Screener",
      icon: Filter,
      status: "idle",
      description: "Filters and ranks stocks by criteria"
    },
    {
      id: "recommender",
      name: "Recommender",
      icon: Target,
      status: "idle",
      description: "Provides buy/sell recommendations"
    },
    {
      id: "buy",
      name: "Buy Agent",
      icon: ShoppingCart,
      status: "idle",
      description: "Executes purchase transactions"
    },
    {
      id: "sell",
      name: "Sell Agent",
      icon: DollarSign,
      status: "idle",
      description: "Executes sale transactions"
    }
  ]);
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "agent",
      content: "Welcome to Industry Agent! I can help you analyze stocks, create visualizations, screen securities, and execute trades. Try asking me to plot a chart, screen stocks, or get recommendations.",
      agentName: "Orchestrator Agent",
      timestamp: new Date().toLocaleTimeString()
    }
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isTyping) return;

    const userMessage: Message = {
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: "user",
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery("");
    setIsTyping(true);

    // Update orchestrator status
    setAgents(prev => prev.map(agent => 
      agent.id === "orchestrator" 
        ? { ...agent, status: "processing" }
        : agent
    ));

    // Process the query
    setTimeout(() => {
      processUserQuery(query);
    }, 1000);
  };

  const processUserQuery = async (userQuery: string) => {
    try {
      // Get token from auth store or localStorage
      const { token: storeToken } = useAuthStore.getState();
      const token = storeToken || localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userQuery
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Determine which agent responded based on agent_name
      const agentId = getAgentIdFromName(data.agent_name);
      
      // Update agent status to processing first
      setAgents(prev => prev.map(agent => 
        agent.id === agentId 
          ? { ...agent, status: "processing" }
          : agent.id === "orchestrator" && agentId !== "orchestrator"
          ? { ...agent, status: "completed" }
          : agent
      ));

      // Create response message with structured data if available
      const agentMessage: Message = {
        id: `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: "agent",
        content: data.message,
        agentName: data.agent_name,
        interactive: data.data ? createInteractiveComponent(data.data, data.agent_name) : undefined,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      // Update agent status to completed
      setAgents(prev => prev.map(agent => 
        agent.id === agentId 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
    } catch (error) {
      console.error('Error calling API:', error);
      
      // Fallback to showing an error message
      const errorMessage: Message = {
        id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: "agent",
        content: "I'm having trouble processing your request right now. Please try again later.",
        agentName: "System",
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, errorMessage]);
      
      // Reset orchestrator status
      setAgents(prev => prev.map(agent => 
        agent.id === "orchestrator" 
          ? { ...agent, status: "completed" }
          : agent
      ));
    }
    
    setIsTyping(false);
  };

  const getAgentIdFromName = (agentName: string): string => {
    if (agentName.toLowerCase().includes('screener')) return 'screener';
    if (agentName.toLowerCase().includes('visualizer')) return 'visualizer';
    if (agentName.toLowerCase().includes('recommender')) return 'recommender';
    if (agentName.toLowerCase().includes('buy')) return 'buy';
    if (agentName.toLowerCase().includes('sell')) return 'sell';
    return 'orchestrator';
  };

  const createInteractiveComponent = (stockData: any[], agentName: string) => {
    if (agentName.toLowerCase().includes('screener') && stockData) {
      return <ScreenerResponseWithData stockData={stockData} onNext={() => triggerRecommender()} />;
    }
    // Add other interactive components as needed
    return null;
  };

  // Custom ScreenerResponse component that uses actual API data
  const ScreenerResponseWithData = ({ stockData, onNext }: { stockData: any[], onNext: () => void }) => (
    <Card className="bg-card-glass/50 border border-accent/20">
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">Screened Stocks</p>
        <div className="space-y-2">
          {stockData.map((stock, i) => (
            <div key={stock.ticker || i} className="flex justify-between items-center p-3 rounded bg-card-glass/30 border border-border/10">
              <div>
                <span className="text-sm font-medium">{stock.ticker} - {stock.name}</span>
                <p className="text-xs text-muted-foreground">Performance: {stock.performance}</p>
              </div>
              <Badge variant={i < 2 ? "default" : "secondary"}>
                {stock.performance}
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

  const startVisualizationWorkflow = (query: string) => {
    // Activate visualizer
    setAgents(prev => prev.map(agent => 
      agent.id === "visualizer" 
        ? { ...agent, status: "processing" }
        : agent.id === "orchestrator"
        ? { ...agent, status: "completed" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "I've analyzed the request and created a performance chart for Tata Motors. The data shows strong quarterly growth.",
        agentName: "Visualizer Agent",
        interactive: (
          <VisualizerResponse onNext={() => triggerScreener()} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "visualizer" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 2000);
  };

  const triggerScreener = () => {
    setIsTyping(true);
    setAgents(prev => prev.map(agent => 
      agent.id === "screener" 
        ? { ...agent, status: "processing" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "I've identified the top 5 performers in the automotive sector. These stocks show strong momentum and volume.",
        agentName: "Screener Agent",
        interactive: (
          <ScreenerResponse onNext={() => triggerRecommender()} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "screener" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 1500);
  };

  const triggerRecommender = () => {
    setIsTyping(true);
    setAgents(prev => prev.map(agent => 
      agent.id === "recommender" 
        ? { ...agent, status: "processing" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "Based on technical analysis, I've generated buy/sell recommendations. The signals are based on RSI, MACD, and trend analysis.",
        agentName: "Recommender Agent",
        interactive: (
          <RecommenderResponse onNext={() => executeTrade()} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "recommender" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 2000);
  };

  const executeTrade = () => {
    setIsTyping(true);
    setAgents(prev => prev.map(agent => 
      agent.id === "buy" 
        ? { ...agent, status: "processing" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "Trade execution completed successfully. Your portfolio has been updated with the new positions.",
        agentName: "Buy Agent",
        interactive: (
          <TradingResponse type="buy" stocks={["Tata Motors - 50 shares at ₹485", "Mahindra - 20 shares at ₹1,245"]} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "buy" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 1500);
  };

  const startScreeningWorkflow = (query: string) => {
    setAgents(prev => prev.map(agent => 
      agent.id === "screener" 
        ? { ...agent, status: "processing" }
        : agent.id === "orchestrator"
        ? { ...agent, status: "completed" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "I've screened the market based on your criteria. Here are the top performers with strong fundamentals and technical indicators.",
        agentName: "Screener Agent",
        interactive: (
          <ScreenerResponse onNext={() => triggerRecommender()} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "screener" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 2000);
  };

  const startRecommendationWorkflow = (query: string) => {
    setAgents(prev => prev.map(agent => 
      agent.id === "recommender" 
        ? { ...agent, status: "processing" }
        : agent.id === "orchestrator"
        ? { ...agent, status: "completed" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: "I've analyzed the requested securities and generated comprehensive recommendations based on multiple technical indicators.",
        agentName: "Recommender Agent",
        interactive: (
          <RecommenderResponse onNext={() => executeTrade()} />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === "recommender" 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 2000);
  };

  const startDirectTradingWorkflow = (query: string) => {
    const isBuy = query.toLowerCase().includes("buy");
    const agentId = isBuy ? "buy" : "sell";
    
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { ...agent, status: "processing" }
        : agent.id === "orchestrator"
        ? { ...agent, status: "completed" }
        : agent
    ));

    setTimeout(() => {
      const agentMessage: Message = {
        id: Date.now().toString(),
        type: "agent",
        content: `I've executed your ${isBuy ? "purchase" : "sale"} order successfully. The transaction has been completed and your portfolio updated.`,
        agentName: `${isBuy ? "Buy" : "Sell"} Agent`,
        interactive: (
          <TradingResponse 
            type={isBuy ? "buy" : "sell"} 
            stocks={[`RELIANCE - 25 shares at ₹${isBuy ? "2,450" : "2,475"}`]} 
          />
        ),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      setAgents(prev => prev.map(agent => 
        agent.id === agentId 
          ? { ...agent, status: "completed" }
          : agent
      ));
      
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border/20 bg-card-glass/50 backdrop-blur-sm flex-shrink-0">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Brain className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-xl font-bold">Industry Agent</h1>
              <p className="text-sm text-muted-foreground">AI Trading Platform</p>
            </div>
          </div>
          <Button
            variant="ghost"
            onClick={handleLogout}
            className="text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            <div className="max-w-4xl mx-auto space-y-4">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  type={message.type}
                  content={message.content}
                  agentName={message.agentName}
                  interactive={message.interactive}
                  timestamp={message.timestamp}
                />
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] space-y-2">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Sparkles className="h-4 w-4 animate-spin" />
                      <span>AI is thinking...</span>
                    </div>
                    <div className="bg-card-glass/80 backdrop-blur-sm border border-border/20 p-4 rounded-2xl rounded-tl-md shadow-glass">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-border/20 bg-card-glass/30 backdrop-blur-sm p-6 flex-shrink-0">
            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSubmit} className="flex gap-4">
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask me to plot charts, screen stocks, or make trading decisions..."
                  className="flex-1 bg-card-glass/50 border-border/20 text-base h-12"
                  disabled={isTyping}
                />
                <Button 
                  type="submit" 
                  size="lg"
                  variant="secondary"
                  disabled={isTyping || !query.trim()}
                  className="px-6"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </div>
        </div>

        {/* Agent Sidebar */}
        <AgentSidebar agents={agents} />
      </div>
    </div>
  );
};

export default Playground;