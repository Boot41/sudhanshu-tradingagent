import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Brain, TrendingUp, BarChart3, Eye, Filter, Target, ShoppingCart, DollarSign } from "lucide-react";
import { useNavigate } from "react-router-dom";
import heroImage from "@/assets/hero-trading.jpg";
import RegisterForm from "@/components/RegisterForm";

const Landing = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Mock login process
    setTimeout(() => {
      navigate("/playground");
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-hero relative overflow-hidden">
      {/* Hero Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
        style={{ backgroundImage: `url(${heroImage})` }}
      />
      <div className="absolute inset-0 bg-gradient-hero/80" />
      
      <div className="relative z-10 flex items-center justify-center p-6 min-h-screen">
        <div className="w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        
          {/* Hero Section */}
          <div className="space-y-8 animate-fade-in">
            <div className="space-y-4">
              <h1 className="text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                Industry Agent
              </h1>
              <p className="text-xl text-muted-foreground leading-relaxed">
                AI-powered trading platform with intelligent agents for visualization, screening, 
                recommendations, and automated trading decisions.
              </p>
            </div>

            {/* Agent Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { icon: Eye, name: "Visualizer", desc: "Charts & graphs" },
                { icon: Filter, name: "Screener", desc: "Stock filtering" },
                { icon: Target, name: "Recommender", desc: "Buy/sell signals" },
                { icon: ShoppingCart, name: "Buy Agent", desc: "Purchase execution" },
                { icon: DollarSign, name: "Sell Agent", desc: "Sale execution" },
                { icon: Brain, name: "Orchestrator", desc: "AI coordination" }
              ].map((agent, index) => (
                <div 
                  key={agent.name}
                  className="p-4 rounded-lg bg-card-glass/30 backdrop-blur-sm border border-border/20 text-center space-y-2 hover:bg-card-glass/50 transition-all duration-300"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <agent.icon className="h-6 w-6 text-primary mx-auto" />
                  <div>
                    <p className="font-medium text-sm">{agent.name}</p>
                    <p className="text-xs text-muted-foreground">{agent.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-4 p-4 rounded-lg bg-primary/10 border border-primary/20">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Generative UX</p>
                <p className="text-sm text-muted-foreground">Dynamic workflows that adapt to your trading style</p>
              </div>
            </div>
          </div>

          {/* Login/Register Form */}
          {showRegister ? (
            <RegisterForm onLoginClick={() => setShowRegister(false)} />
          ) : (
            <div className="animate-slide-in-right">
              <Card className="bg-card-glass/80 backdrop-blur-sm border border-border/20 shadow-glass">
                <CardHeader className="text-center space-y-2">
                  <div className="mx-auto p-3 rounded-full bg-primary/10">
                    <BarChart3 className="h-8 w-8 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">Welcome Back</CardTitle>
                  <CardDescription>
                    Access your AI trading dashboard
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="trader@example.com"
                        required
                        className="bg-card-glass/50 border-border/20"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="password">Password</Label>
                      <Input
                        id="password"
                        type="password"
                        required
                        className="bg-card-glass/50 border-border/20"
                      />
                    </div>
                    <Button
                      type="submit"
                      variant="hero"
                      className="w-full"
                      disabled={isLoading}
                    >
                      {isLoading ? "Connecting..." : "Enter Trading Platform"}
                    </Button>
                  </form>
                  <p className="text-center text-sm text-muted-foreground mt-4">
                    Don't have an account?{" "}
                    <Button variant="link" className="p-0 h-auto text-primary" onClick={() => setShowRegister(true)}>
                      Sign Up
                    </Button>
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Landing;