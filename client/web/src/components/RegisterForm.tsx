import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UserPlus, AlertCircle } from 'lucide-react';
import { useAuthStore } from "@/store/authStore";
import { useNavigate } from "react-router-dom";

interface RegisterFormProps {
  onLoginClick: () => void;
}

const RegisterForm = ({ onLoginClick }: RegisterFormProps) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    phone: ""
  });
  
  const navigate = useNavigate();
  const { register, isLoading, error, isAuthenticated, clearError } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/playground");
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const success = await register(formData);
    if (success) {
      navigate("/playground");
    }
  };

  const isFormValid = formData.username && formData.email && formData.password && formData.phone;

  return (
    <div className="animate-slide-in-left">
      <Card className="bg-card-glass/80 backdrop-blur-sm border border-border/20 shadow-glass">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto p-3 rounded-full bg-primary/10">
            <UserPlus className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">Create an Account</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input 
                id="username" 
                name="username"
                type="text" 
                placeholder="yourusername" 
                value={formData.username}
                onChange={handleInputChange}
                required 
                className="bg-card-glass/50 border-border/20"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                name="email"
                type="email" 
                placeholder="trader@example.com" 
                value={formData.email}
                onChange={handleInputChange}
                required 
                className="bg-card-glass/50 border-border/20"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                name="password"
                type="password" 
                value={formData.password}
                onChange={handleInputChange}
                required 
                className="bg-card-glass/50 border-border/20"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input 
                id="phone" 
                name="phone"
                type="tel" 
                placeholder="+1234567890" 
                value={formData.phone}
                onChange={handleInputChange}
                required 
                className="bg-card-glass/50 border-border/20"
                disabled={isLoading}
              />
            </div>
            <Button 
              type="submit" 
              variant="hero" 
              className="w-full"
              disabled={isLoading || !isFormValid}
            >
              {isLoading ? "Creating Account..." : "Register"}
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Already have an account?{" "}
            <Button variant="link" className="p-0 h-auto text-primary" onClick={onLoginClick}>
              Login
            </Button>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegisterForm;
