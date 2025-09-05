import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChatMessage, VisualizerResponse, ScreenerResponse, RecommenderResponse, TradingResponse } from "@/components/ChatMessage";
import { TradingAnalysisDisplay } from "@/components/TradingAnalysisDisplay";
import { AgentSidebar } from "@/components/AgentSidebar";
import { 
  Brain, Eye, Filter, Target, ShoppingCart, DollarSign, 
  Send, LogOut, Sparkles, ArrowRight, BarChart3, TrendingUp,
  Users, Newspaper, FileText
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
      id: "coordinator",
      name: "Marcus Wellington",
      icon: Brain,
      status: "idle",
      description: "Senior Trading Strategist with 15+ years experience in quantitative analysis and portfolio management"
    },
    {
      id: "ticker",
      name: "Ticker Agent",
      icon: Target,
      status: "idle",
      description: "Validates and resolves company names to tickers"
    },
    {
      id: "fundamentals",
      name: "Fundamentals Agent",
      icon: BarChart3,
      status: "idle",
      description: "Analyzes company financials and ratios"
    },
    {
      id: "technical",
      name: "Technical Agent",
      icon: TrendingUp,
      status: "idle",
      description: "Calculates technical indicators and trends"
    },
    {
      id: "sentiment",
      name: "Sentiment Agent",
      icon: Users,
      status: "idle",
      description: "Analyzes news sentiment and market mood"
    },
    {
      id: "news",
      name: "News Agent",
      icon: Newspaper,
      status: "idle",
      description: "Evaluates news events and market impact"
    },
    {
      id: "research",
      name: "Research Manager",
      icon: FileText,
      status: "idle",
      description: "Synthesizes bull/bear research perspectives"
    },
    {
      id: "trader",
      name: "Trader Agent",
      icon: DollarSign,
      status: "idle",
      description: "Makes final trading decisions with risk management"
    }
  ]);
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "agent",
      content: "Hello! I'm Marcus Wellington, your AI Trading Strategist. I specialize in comprehensive market analysis, risk assessment, and trading recommendations. I can analyze any stock using advanced technical indicators, fundamental analysis, sentiment tracking, and news impact assessment. What company would you like me to analyze today?",
      agentName: "Marcus Wellington",
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

    // Update coordinator status
    setAgents(prev => prev.map(agent => 
      agent.id === "coordinator" 
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
          : agent.id === "coordinator" && agentId !== "coordinator"
          ? { ...agent, status: "completed" }
          : agent
      ));

      // Create response message with structured data if available
      const agentMessage: Message = {
        id: `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: "agent",
        content: data.message,
        agentName: data.agent_name,
        interactive: data.trading_analysis ? createInteractiveComponent(data.trading_analysis, data.agent_name) : 
                    data.data ? createInteractiveComponent(data.data, data.agent_name) : undefined,
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
      
      // Reset coordinator status
      setAgents(prev => prev.map(agent => 
        agent.id === "coordinator" 
          ? { ...agent, status: "completed" }
          : agent
      ));
    }
    
    setIsTyping(false);
  };

  const getAgentIdFromName = (agentName: string): string => {
    if (agentName.toLowerCase().includes('ticker')) return 'ticker';
    if (agentName.toLowerCase().includes('fundamentals')) return 'fundamentals';
    if (agentName.toLowerCase().includes('technical')) return 'technical';
    if (agentName.toLowerCase().includes('sentiment')) return 'sentiment';
    if (agentName.toLowerCase().includes('news')) return 'news';
    if (agentName.toLowerCase().includes('research')) return 'research';
    if (agentName.toLowerCase().includes('trader')) return 'trader';
    return 'coordinator';
  };

  const createInteractiveComponent = (data: any, agentName: string) => {
    // Handle trading analysis data (single object with workflow_id property)
    if (data && typeof data === 'object' && 'workflow_id' in data) {
      return <TradingAnalysisDisplay data={data} />;
    }
    // Handle stock data arrays - add other components as needed
    if (Array.isArray(data)) {
      // Future: add components for stock screening results
      return null;
    }
    return null;
  };

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border/20 bg-card-glass/50 backdrop-blur-sm flex-shrink-0">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Brain className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold">TradingAgent Pro</h1>
              <p className="text-base text-muted-foreground">AI-Powered Trading Analysis Platform</p>
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
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Sparkles className="h-4 w-4 animate-spin" />
                      <span>Marcus is analyzing the market...</span>
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
                  placeholder="Enter a company name or ticker symbol for comprehensive trading analysis..."
                  className="flex-1 bg-card-glass/50 border-border/20 text-lg h-14"
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